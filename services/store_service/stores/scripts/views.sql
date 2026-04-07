CREATE VIEW IF NOT EXISTS user_orders AS
SELECT
    u.username,
    p.name,
    it.quantity
FROM stores_user u
 JOIN stores_order o ON u.id = o.user_id
 JOIN stores_orderitem it ON o.order_id = it.order_id
 JOIN stores_product p ON it.product_id = p.id;
