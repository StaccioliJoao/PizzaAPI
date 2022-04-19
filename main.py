from fastapi import FastAPI, Query, HTTPException, Path
from pydantic import BaseModel
from typing import Optional
import json
from datetime import datetime
app = FastAPI()


class order(BaseModel):
    flavor: str
    order_num: Optional[int] = None
    crust: Optional[str] = "Normal"
    size: str
    table_num: int
    timestamp: Optional[str] = None


with open("orders.json", "r") as f:
    orders = json.load(f)


@app.get("/orders/{o_id}")
def get_order(o_id: int):
    for order in orders:
        if order['order_num'] == o_id:
            return order
    raise HTTPException(status_code=404, detail="Order not found")


@app.get("/tableOrders/{t_id}")
def get_tableOrders(t_id: int):
    table_orders = []
    for order in orders:
        if order['table_num'] == t_id:
            table_orders.append(order)
    if len(table_orders) == 0:
        raise HTTPException(status_code=404, detail="Table not found")
    return table_orders


@app.get("/search", status_code=200)
def search_order(flavor: Optional[str] = Query(None, title="Flavor", description="Flavor to filter for"),
                 crust: Optional[str] = Query(None, title="Crust", description="Crust to filter for"),
                 size: Optional[str] = Query(None, title="Size", description="Size to filter for")):
    filtered_orders = []
    for order in orders:
        if flavor is None or flavor.lower() in order['flavor'].lower():
            if crust is None or crust.lower() in order['crust'].lower():
                if size is None or size.lower() in order['size'].lower():
                    filtered_orders.append(order)
    return filtered_orders


@app.post("/addOrder", status_code=201)
def add_order(order: order):
    order_id = max([o['order_num'] for o in orders]) + 1
    new_order = {
        'flavor': order.flavor,
        'order_num': order_id,
        'crust': order.crust,
        'size': order.size,
        'table_num': order.table_num,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    orders.append(new_order)
    with open("orders.json", "w") as f:
        json.dump(orders, f)

    return new_order


@app.put("/updateOrder/", status_code=204)
def change_order(order: order):
    new_order = {
        'flavor': order.flavor,
        'order_num': order.order_num,
        'crust': order.crust,
        'size': order.size,
        'table_num': order.table_num,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    order_list = [o for o in orders if o['order_num'] == order.order_num]
    if len(order_list) > 0:
        orders.remove(order_list[0])
        orders.append(new_order)
        with open("orders.json", "w") as f:
            json.dump(orders, f)
        return new_order
    else:
        raise HTTPException(status_code=404, detail="Order not found")


@app.delete("/deleteOrder/{o_id}", status_code=204)
def delete_order(o_id: int):
    order = [o for o in orders if o['order_num'] == o_id]
    if len(order) > 0:
        orders.remove(order[0])
        with open("orders.json", "w") as f:
            json.dump(orders, f)
    else:
        raise HTTPException(status_code=404, detail="Order not found")
