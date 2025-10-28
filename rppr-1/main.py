from fastapi import FastAPI, HTTPException
from models import OperationRequest, ExpressionRequest, ExpressionResponse, CalculatorState
from calculator import Calculator
import re

app = FastAPI(title="Калькулятор выражений", version="1.0.0")

calculator = Calculator()


@app.get("/")
async def root():
    return {"message": "Добро пожаловать в калькулятор выражений!"}


@app.post("/operation", response_model=ExpressionResponse)
async def perform_operation(request: OperationRequest):
    """Выполнение базовой операции между двумя числами"""
    try:
        result = calculator.basic_operation(request.a, request.b, request.operation)

        # Обновляем текущее выражение
        expr = f"({request.a} {request.operation} {request.b})"
        calculator.current_expression = expr

        return ExpressionResponse(
            expression=expr,
            result=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ZeroDivisionError:
        raise HTTPException(status_code=400, detail="Деление на ноль")


@app.post("/expression", response_model=ExpressionResponse)
async def evaluate_expression(request: ExpressionRequest):
    """Вычисление сложного выражения"""
    try:
        result = calculator.evaluate_expression(request.expression)
        calculator.current_expression = request.expression

        return ExpressionResponse(
            expression=request.expression,
            result=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@app.post("/variable/{name}/{value}")
async def set_variable(name: str, value: float):
    """Установка значения переменной"""
    calculator.set_variable(name, value)
    return {"message": f"Переменная {name} установлена в {value}"}


@app.get("/state", response_model=CalculatorState)
async def get_state():
    """Просмотр текущего состояния выражения и переменных"""
    state = calculator.get_state()
    return CalculatorState(
        current_expression=state['current_expression'],
        variables=state['variables']
    )


@app.post("/execute", response_model=ExpressionResponse)
async def execute_expression():
    """Выполнение текущего выражения"""
    if not calculator.current_expression:
        raise HTTPException(status_code=400, detail="Нет текущего выражения для выполнения")

    try:
        result = calculator.evaluate_expression(calculator.current_expression)

        return ExpressionResponse(
            expression=calculator.current_expression,
            result=result
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка вычисления: {str(e)}")


@app.delete("/clear")
async def clear_calculator():
    """Очистка калькулятора"""
    calculator.clear()
    return {"message": "Калькулятор очищен"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
