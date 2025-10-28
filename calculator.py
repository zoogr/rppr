import re
from typing import Dict, List, Union, Optional

class Calculator:
    def __init__(self):
        self.current_expression = ""
        self.variables = {}
    
    def basic_operation(self, a: float, b: float, operation: str) -> float:
        """Выполнение базовых операций"""
        operations = {
            '+': lambda x, y: x + y,
            '-': lambda x, y: x - y,
            '*': lambda x, y: x * y,
            '/': lambda x, y: x / y if y != 0 else float('inf')
        }
        
        if operation not in operations:
            raise ValueError(f"Неподдерживаемая операция: {operation}")
        
        return operations[operation](a, b)
    
    def parse_expression(self, expression: str) -> List[Union[str, float]]:
        """Парсинг выражения на токены"""
        # Удаляем пробелы и приводим к нижнему регистру
        expression = expression.replace(' ', '').lower()
        
        # Регулярное выражение для парсинга чисел, операторов и переменных
        pattern = r'(\d+\.?\d*|[a-zA-Z_][a-zA-Z0-9_]*|[\+\-\*\/\(\)])'
        tokens = re.findall(pattern, expression)
        
        parsed_tokens = []
        for token in tokens:
            if token.replace('.', '').isdigit():
                parsed_tokens.append(float(token))
            elif token in '+-*/()':
                parsed_tokens.append(token)
            else:
                parsed_tokens.append(token)  # переменная
        
        return parsed_tokens
    
    def evaluate_tokens(self, tokens: List[Union[str, float]]) -> float:
        """Вычисление выражения из токенов с учетом приоритета операций"""
        def apply_operation(operands: List[float], operators: List[str]):
            op = operators.pop()
            b = operands.pop()
            a = operands.pop()
            operands.append(self.basic_operation(a, b, op))
        
        operands = []
        operators = []
        
        i = 0
        while i < len(tokens):
            token = tokens[i]
            
            if isinstance(token, (int, float)):
                operands.append(token)
            elif isinstance(token, str) and token not in '+-*/()':
                # Это переменная
                if token in self.variables:
                    operands.append(self.variables[token])
                else:
                    raise ValueError(f"Неизвестная переменная: {token}")
            elif token == '(':
                operators.append(token)
            elif token == ')':
                while operators and operators[-1] != '(':
                    apply_operation(operands, operators)
                operators.pop()  # Удаляем '('
            elif token in '+-*/':
                while (operators and operators[-1] != '(' and 
                       self.get_priority(operators[-1]) >= self.get_priority(token)):
                    apply_operation(operands, operators)
                operators.append(token)
            
            i += 1
        
        while operators:
            apply_operation(operands, operators)
        
        return operands[0] if operands else 0
    
    def get_priority(self, operator: str) -> int:
        """Получение приоритета оператора"""
        priorities = {
            '+': 1,
            '-': 1,
            '*': 2,
            '/': 2
        }
        return priorities.get(operator, 0)
    
    def evaluate_expression(self, expression: str) -> float:
        """Вычисление строкового выражения"""
        tokens = self.parse_expression(expression)
        return self.evaluate_tokens(tokens)
    
    def set_variable(self, name: str, value: float):
        """Установка значения переменной"""
        self.variables[name] = value
    
    def get_state(self) -> dict:
        """Получение текущего состояния калькулятора"""
        return {
            'current_expression': self.current_expression,
            'variables': self.variables
        }
    
    def clear(self):
        """Очистка калькулятора"""
        self.current_expression = ""
        self.variables = {}