from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from http import HTTPStatus
from typing import Any


@dataclass(slots=True)
class QuantaForgeError(Exception):
    """A user-safe, machine-readable error raised by the agent."""

    code: str
    error_type: str
    message: str
    field: str | None = None
    algorithm: str | None = None
    requested: Any = None
    allowed: Any = None
    recoverable: bool = False
    retryable: bool = False
    suggestions: list[str] = dataclass_field(default_factory=list)
    details: dict[str, Any] = dataclass_field(default_factory=dict)
    http_status: int = HTTPStatus.UNPROCESSABLE_ENTITY

    def __post_init__(self) -> None:
        Exception.__init__(self, self.message)

    def to_error_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "type": self.error_type,
            "message": self.message,
            "http_status": int(self.http_status),
            "recoverable": self.recoverable,
            "retryable": self.retryable,
            "suggestions": self.suggestions,
        }
        optional = {
            "field": self.field,
            "algorithm": self.algorithm,
            "requested": self.requested,
            "allowed": self.allowed,
        }
        payload.update({key: value for key, value in optional.items() if value is not None})
        if self.details:
            payload["details"] = self.details
        return payload


def capability_limit_error(
    *,
    algorithm: str,
    field_name: str,
    requested: Any,
    minimum: int,
    maximum: int,
    label: str,
    task_id: str | None = None,
) -> QuantaForgeError:
    suggestion = f"将{label}调整到{minimum}至{maximum}"
    details = {"task_id": task_id} if task_id else {}
    return QuantaForgeError(
        code="CAPABILITY_LIMIT_EXCEEDED",
        error_type="validation_error",
        message=(
            f"请求的{algorithm.upper()}{label}为{requested}，"
            f"超出当前允许范围{minimum}至{maximum}。"
        ),
        field=field_name,
        algorithm=algorithm,
        requested=requested,
        allowed={"min": minimum, "max": maximum},
        recoverable=True,
        suggestions=[suggestion, "修改请求后重新提交，当前请求未启动量子执行"],
        details=details,
    )


def invalid_parameter_error(
    *,
    code: str,
    message: str,
    field_name: str,
    requested: Any,
    allowed: Any,
    algorithm: str | None = None,
    suggestions: list[str] | None = None,
    task_id: str | None = None,
) -> QuantaForgeError:
    details = {"task_id": task_id} if task_id else {}
    return QuantaForgeError(
        code=code,
        error_type="validation_error",
        message=message,
        field=field_name,
        algorithm=algorithm,
        requested=requested,
        allowed=allowed,
        recoverable=True,
        suggestions=suggestions or ["修正参数后重新提交，当前请求未启动量子执行"],
        details=details,
    )


def normalize_error(exc: Exception, *, execution: bool = False) -> QuantaForgeError:
    if isinstance(exc, QuantaForgeError):
        return exc
    if execution:
        return QuantaForgeError(
            code="BACKEND_EXECUTION_FAILED",
            error_type="execution_error",
            message="量子后端执行失败，未生成成功结论。",
            recoverable=True,
            retryable=True,
            suggestions=["检查UnitaryLab与设备环境", "可切换CPU进行诊断后重试"],
            details={"exception_type": type(exc).__name__, "reason": str(exc)},
            http_status=HTTPStatus.SERVICE_UNAVAILABLE,
        )
    return QuantaForgeError(
        code="INTERNAL_ERROR",
        error_type="internal_error",
        message="服务处理请求时发生内部错误。",
        recoverable=False,
        retryable=True,
        suggestions=["保留任务输入和时间戳后重试或联系维护者"],
        details={"exception_type": type(exc).__name__},
        http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def error_response(exc: Exception) -> dict[str, Any]:
    structured = normalize_error(exc)
    task_id = structured.details.get("task_id")
    return {
        "status": "failed",
        "task_id": task_id,
        "summary": f"请求未执行：{structured.message}",
        "plan": [],
        "metrics": {},
        "verification": {"passed": False, "executed": False},
        "artifacts": {},
        "warnings": [],
        "error": structured.to_error_dict(),
    }
