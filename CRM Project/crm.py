import json
import os
from decimal import Decimal
from abc import ABC, abstractmethod
from typing import List, Dict


class Entity(ABC):
    """Абстрактный класс для всех сущностей CRM."""

    def __init__(self, id: str, name: str) -> None:
        """Конструктор для сущности.

        Args:
            id: уникальный идентификатор сущности.
            name: имя сущности.
        """
        self.id = id
        self.name = name

    @abstractmethod
    def to_dict(self) -> dict:
        """Абстрактный метод для преобразования данных сущности в словарь."""
        pass


class Product:
    """Класс товара."""

    def __init__(
            self,
            id: str = "None",
            name: str = "None",
            count: int = 0,
            state: str = "None",
            provider: str = "None",
            manufacturer: str = "None",
            cost: Decimal = Decimal("0.00"),
            location: str = "None",
            city: str = "None"
    ) -> None:
        """Конструктор класса.

        Args:
            id: идентификатор.
            name: название.
            count: количество.
            state: состояние.
            provider: поставщик.
            manufacturer: производитель.
            cost: стоимость.
            location: местоположение.
            city: город.
        """
        self.id = id
        self.name = name
        self.count = int(count)
        self.state = state
        self.provider = provider
        self.manufacturer = manufacturer
        self.cost = Decimal(str(cost))
        self.location = location
        self.city = city

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {
            "id": self.id, "name": self.name, "count": self.count,
            "state": self.state, "provider": self.provider,
            "manufacturer": self.manufacturer, "cost": str(self.cost),
            "location": self.location, "city": self.city
        }


# --- ПЕРСОНАЛ И ПОКУПАТЕЛИ ---

class Employee(Entity):
    """Класс сотрудника."""

    def __init__(self, id: str, name: str, role: str, salary: Decimal) -> None:
        """Конструктор класса.

        Args:
            role: должность.
            salary: зарплата.
        """
        super().__init__(id, name)
        self.role = role
        self.salary = Decimal(str(salary))

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {"id": self.id, "name": self.name, "role": self.role, "salary": str(self.salary)}


class Order:
    """Класс заказа для учета продаж."""

    def __init__(self, order_id: str, product_id: str, product_name: str, count: int, total_price: Decimal,
                 pos_id: str) -> None:
        """Конструктор класса.

        Args:
            order_id: id заказа.
            product_id: id товара.
            product_name: имя товара.
            count: количество товара.
            total_price: итоговая стоимость заказа.
            pos_id: id пункта продаж.
        """
        self.order_id = order_id
        self.product_id = product_id
        self.product_name = product_name  # Сохраняем имя для корректного возврата
        self.count = count
        self.total_price = total_price
        self.pos_id = pos_id

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {
            "order_id": self.order_id, "product_id": self.product_id,
            "product_name": self.product_name, "count": self.count,
            "total_price": str(self.total_price), "pos_id": self.pos_id
        }


class BusinessUnit(Entity):
    """Базовый класс описания предприятий (магазины/склады)."""

    def __init__(self, id: str, name: str, address: str) -> None:
        """Конструктор класса.

        Args:
            address: адрес предприятия.
        """
        super().__init__(id, name)
        self.address = address
        self.responsible_id = "None"
        self.balance = Decimal("0.00")


class WarehouseCell:
    """Класс ячейки хранения на складе."""

    def __init__(self, cell_id: str) -> None:
        """Конструктор класса.

        Args:
            cell_id: идентификатор ячейки.
        """
        self.cell_id = cell_id
        self.products: List[Product] = []

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {"cell_id": self.cell_id, "products": [p.to_dict() for p in self.products]}


class Warehouse(BusinessUnit):
    """Класс склада."""

    def __init__(self, id: str, name: str, address: str) -> None:
        """Конструктор класса."""
        super().__init__(id, name, address)
        self.cells: Dict[str, WarehouseCell] = {}

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {
            "id": self.id, "name": self.name, "address": self.address,
            "responsible_id": self.responsible_id, "cells": {k: v.to_dict() for k, v in self.cells.items()}
        }


class PointOfSale(BusinessUnit):
    """Класс пункта продаж (магазина)."""

    def __init__(self, id: str, name: str, address: str) -> None:
        """Конструктор класса."""
        super().__init__(id, name, address)
        self.inventory: List[Product] = []

    def to_dict(self) -> dict:
        """Преобразование полей объекта в словарь.

        Returns:
            Словарь с данными объекта.
        """

        return {
            "id": self.id, "name": self.name, "address": self.address,
            "balance": str(self.balance), "responsible_id": self.responsible_id,
            "inventory": [p.to_dict() for p in self.inventory]
        }


class CRMSystem:
    """Класс основной логики работы CRM."""

    def __init__(self) -> None:
        """Конструктор класса."""
        self.db_file = "crm_database.json"
        self.catalog_file = "catalog.json"
        self.warehouses: Dict[str, Warehouse] = {}
        self.pos: Dict[str, PointOfSale] = {}
        self.employees: Dict[str, Employee] = {}
        self.orders: Dict[str, Order] = {}
        self.total_profit = Decimal("0.00")
        self.catalog = []
        self.load_all()

    def load_all(self) -> None:
        """Десереализация прошлых сохраненных данных из файлов json."""
        if not os.path.exists(self.catalog_file):
            self.catalog = []
            self.save_catalog()
        else:
            with open(self.catalog_file, 'r', encoding='utf-8') as f:
                self.catalog = json.load(f)

        if os.path.exists(self.db_file):
            with open(self.db_file, 'r', encoding='utf-8') as f:
                d = json.load(f)
                self.total_profit = Decimal(d.get("profit", "0"))
                for k, v in d.get("employees", {}).items():
                    self.employees[k] = Employee(k, v['name'], v['role'], Decimal(v['salary']))
                for k, v in d.get("warehouses", {}).items():
                    wh = Warehouse(k, v['name'], v['address'])
                    wh.responsible_id = v['responsible_id']
                    for cid, cdata in v.get("cells", {}).items():
                        cell = WarehouseCell(cid)
                        for p in cdata['products']: cell.products.append(Product(**p))
                        wh.cells[cid] = cell
                    self.warehouses[k] = wh
                for k, v in d.get("pos", {}).items():
                    ps = PointOfSale(k, v['name'], v['address'])
                    ps.balance = Decimal(v['balance']);
                    ps.responsible_id = v['responsible_id']
                    for p in v.get("inventory", []): ps.inventory.append(Product(**p))
                    self.pos[k] = ps
                for k, v in d.get("orders", {}).items():
                    self.orders[k] = Order(k, v['product_id'], v['product_name'], v['count'], Decimal(v['total_price']),
                                           v['pos_id'])

    def save_all(self) -> None:
        """Сохранение текущего состояния программы в json."""
        data = {
            "profit": str(self.total_profit),
            "employees": {k: v.to_dict() for k, v in self.employees.items()},
            "warehouses": {k: v.to_dict() for k, v in self.warehouses.items()},
            "pos": {k: v.to_dict() for k, v in self.pos.items()},
            "orders": {k: v.to_dict() for k, v in self.orders.items()}
        }
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        self.save_catalog()

    def save_catalog(self) -> None:
        """Сохранение каталога поставщиков в json."""
        with open(self.catalog_file, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=4, ensure_ascii=False)

    # --- ЛОГИКА ОПЕРАЦИЙ ---

    def hire_employee(self, id, name, role, salary) -> str:
        """Найм сотрудника.

        Args:
            id: id сотрудника.
            name: имя.
            role: должность.
            salary: зарплата.
        """
        self.employees[id] = Employee(id, name, role, Decimal(salary))

        return "Сотрудник нанят."

    def fire_employee(self, eid) -> str:
        """Увольнение с очисткой связей.

        Args:
            eid: id сотрудника.
        """
        if eid not in self.employees:

            return "Не найден."

        for u in list(self.warehouses.values()) + list(self.pos.values()):
            if u.responsible_id == eid:
                u.responsible_id = "None"
        del self.employees[eid]

        return "Сотрудник уволен."

    def purchase(self, idx, wid, count) -> str:
        """Логика закупки.

        Args:
            idx: порядковый номер товара в каталоге поставщика.
            wid: id склада.
            count: количество товара.
        """
        if wid not in self.warehouses:

            return "Склад не найден."

        item = self.catalog[idx]
        if item['available'] < count:

            return "Нет у поставщика."

        item['available'] -= count
        wh = self.warehouses[wid]
        cid = f"Cell-{item['id']}"
        if cid not in wh.cells:
            wh.cells[cid] = WarehouseCell(cid)

        wh.cells[cid].products.append(
            Product(id=item['id'], name=item['name'], count=count, cost=Decimal(item['cost'])))
        self.total_profit -= Decimal(item['cost']) * count

        self.save_all()

        return "Закуплено."

    def transfer(self, wid, pid, prod_id, count) -> str:
        """Логика перемещения товара со склада в магазин.

        Args:
            wid: id склада.
            pid: id пункта продаж.
            prod_id: id товара.
            count: количество товара.
        """
        if wid not in self.warehouses or pid not in self.pos:

            return "Ошибка ID."

        wh = self.warehouses[wid]
        ps = self.pos[pid]
        found = False
        for cell in wh.cells.values():
            for product in cell.products:
                if product.id == prod_id and product.count >= count:
                    product.count -= count
                    merged = False
                    for existing in ps.inventory:
                        if existing.id == prod_id:
                            existing.count += count
                            merged = True
                            break
                    if not merged:
                        ps.inventory.append(Product(id=product.id, name=product.name, count=count, cost=product.cost))
                    found = True
                    break

        return "Успешно." if found else "Товар не найден."

    def sell(self, pid, prod_id, count, price) -> str:
        """Логика продажи.

        Args:
            pid: id пункта продаж.
            prod_id: id товара.
            count: количество товара для продажи.
            price: цена за штуку товара.
        """
        if pid not in self.pos:

            return "Магазин не найден."

        ps = self.pos[pid]
        for p in ps.inventory:
            if p.id == prod_id and p.count >= count:
                p.count -= count
                total = Decimal(price) * count
                oid = f"ORD-{len(self.orders) + 100}"
                self.orders[oid] = Order(oid, prod_id, p.name, count, total, pid)
                ps.balance += total
                self.total_profit += total

                return f"Продано! Чек: {oid}"

        return "Ошибка остатков."

    def return_order(self, oid) -> str:
        """Возврат с восстановлением имени и слиянием.

        Args:
            oid: id заказа.
        """
        if oid not in self.orders:

            return "Заказ не найден."

        order = self.orders.pop(oid)
        ps = self.pos[order.pos_id]
        ps.balance -= order.total_price
        self.total_profit -= order.total_price
        found = False
        for p in ps.inventory:
            if p.id == order.product_id:
                p.count += order.count
                found = True
                break
        if not found:
            ps.inventory.append(Product(id=order.product_id, name=order.product_name, count=order.count))

        return f"Товар {order.product_name} возвращен в магазин."


def safe_dec(cost) -> Decimal:
    """Безопасный ввод Decimal.

    Args:
        cost: ввод пользователя.
    """
    while True:
        try:
            return Decimal(input(cost))
        except:
            print("Введите число.")


def safe_int(count) -> int:
    """Безопасный ввод целого числа.

    Args:
        count: ввод пользователя.
    """
    while True:
        try:
            return int(input(count))
        except:
            print("Введите целое число.")


def main() -> None:
    """UI"""
    crm = CRMSystem()
    while True:
        print(f"\n[ CRM ПРИБЫЛЬ: {crm.total_profit} ]")
        print("1. Склады | 2. Магазины | 3. Персонал | 4. Закупки | 5. История Заказов | 6. Доходность | 7. Выход")
        c = input("> ")

        if c == "1":
            while True:
                print("\n- СКЛАДЫ -")
                print("1. Список 2. Открыть 3. Закрыть 4. Содержимое 0. Назад")
                s = input(">> ")
                if s == "0":
                    break
                elif s == "1":
                    for w in crm.warehouses.values():
                        res = crm.employees.get(w.responsible_id)
                        print(f"ID:{w.id} | {w.name} | Отв: {res.name if res else '---'}")
                elif s == "2":
                    i, n, a = input("ID: "), input("Имя: "), input("Адрес: ")
                    crm.warehouses[i] = Warehouse(i, n, a)
                elif s == "3":
                    i = input("ID склада: ")
                    if i in crm.warehouses: del crm.warehouses[i]
                elif s == "4":
                    i = input("ID склада: ")
                    if i in crm.warehouses:
                        for cid, cell in crm.warehouses[i].cells.items():
                            print(
                                f" Ячейка {cid}: {[f'{p.name} ID:{p.id} (x{p.count})' for p in cell.products if p.count > 0]}")

        elif c == "2":
            while True:
                print("\n- МАГАЗИНЫ -")
                print("1. Список 2. Открыть 3. Закрыть 4. Продажа 5. Возврат 6. Перемещение 7. Инвентарь 0. Назад")
                s = input(">> ")
                if s == "0":
                    break
                elif s == "1":
                    for p in crm.pos.values():
                        res = crm.employees.get(p.responsible_id)
                        print(f"ID:{p.id} | {p.name} | Отв: {res.name if res else '---'} | Баланс: {p.balance}")
                elif s == "2":
                    i, n, a = input("ID: "), input("Имя: "), input("Адрес: ")
                    crm.pos[i] = PointOfSale(i, n, a)
                elif s == "3":
                    i = input("ID магазина: ")
                    if i in crm.pos: del crm.pos[i]
                elif s == "4":
                    print(crm.sell(input("ID магазина: "), input("ID товара: "), safe_int("Кол-во: "),
                                   safe_dec("Цена: ")))
                elif s == "5":
                    print(crm.return_order(input("ID заказа: ")))
                elif s == "6":
                    print(crm.transfer(input("ID склада: "), input("ID магазина: "), input("ID товара: "),
                                       safe_int("Кол-во: ")))
                elif s == "7":
                    i = input("ID магазина: ")
                    if i in crm.pos:
                        for p in crm.pos[i].inventory:
                            if p.count > 0: print(f" - {p.name} [ID:{p.id}] x{p.count}")

        elif c == "3":
            while True:
                print("\n- ПЕРСОНАЛ -")
                print("1. Список 2. Найм 3. Уволить 4. Назначить ответственным 0. Назад")
                s = input(">> ")
                if s == "0":
                    break
                elif s == "1":
                    for e in crm.employees.values(): print(f"[{e.id}] {e.name} ({e.role})")
                elif s == "2":
                    print(crm.hire_employee(input("ID: "), input("Имя: "), input("Роль: "), safe_dec("ЗП: ")))
                elif s == "3":
                    print(crm.fire_employee(input("ID сотрудника: ")))
                elif s == "4":
                    eid, uid = input("ID сотрудника: "), input("ID объекта: ")
                    target = crm.warehouses.get(uid) or crm.pos.get(uid)
                    if target and eid in crm.employees: target.responsible_id = eid

        elif c == "4":
            while True:
                crm.load_all()
                print("\n- ЗАКУПКИ (КАТАЛОГ) -")
                for i, item in enumerate(crm.catalog, 1):
                    print(
                        f"{i}. {item['name']} [ID:{item['id']}] | Цена: {item['cost']} | Доступно: {item['available']}")
                print("0. Назад")
                cmd = input("Номер: ")
                if cmd == "0": break
                try:
                    idx = int(cmd) - 1
                    print(crm.purchase(idx, input("ID склада: "), safe_int("Кол-во: ")))
                except:
                    print("Ошибка.")

        elif c == "5":
            while True:
                print("\n- ИСТОРИЯ ЗАКАЗОВ -")
                print("1. Посмотреть всё 2. Удалить заказ 3. Очистить историю 0. Назад")
                s = input(">> ")
                if s == "0":
                    break
                elif s == "1":
                    for o in crm.orders.values(): print(
                        f"Чек:{o.order_id} | Товар:{o.product_name} | Кол-во:{o.count} | Сумма:{o.total_price}")
                elif s == "2":
                    i = input("ID заказа для удаления: ")
                    if i in crm.orders: del crm.orders[i]
                elif s == "3":
                    crm.orders.clear()
                    print("История очищена.")

        elif c == "6":
            print("\n- ОТЧЕТ ДОХОДНОСТИ -")
            for p in crm.pos.values(): print(f"Магазин {p.name}: {p.balance} руб.")
            print(f"ИТОГО ПО КОМПАНИИ: {crm.total_profit} руб.")

        elif c == "7":
            crm.save_all()
            break


if __name__ == "__main__":
    main()
