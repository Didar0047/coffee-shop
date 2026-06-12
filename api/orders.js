// api/orders.js — Vercel Serverless Function
// POST /api/orders  — создать заказ
// GET  /api/orders  — список заказов (требует ADMIN_TOKEN)

const { createClient } = require('@supabase/supabase-js');

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

module.exports = async (req, res) => {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // ── POST: создать заказ ──────────────────────────────────────────────────
  if (req.method === 'POST') {
    const {
      customer_name,
      phone,
      product_name,
      category,
      price,
      size = 'medium',
      quantity = 1,
      delivery_type = 'pickup',
      address = null,
      comment = null,
      source = 'web'
    } = req.body || {};

    // Валидация обязательных полей
    if (!customer_name || !phone || !product_name || !category) {
      return res.status(400).json({
        success: false,
        error: 'Обязательные поля: customer_name, phone, product_name, category'
      });
    }

    if (phone.replace(/\D/g, '').length < 10) {
      return res.status(400).json({
        success: false,
        error: 'Некорректный номер телефона'
      });
    }

    if (delivery_type === 'delivery' && !address) {
      return res.status(400).json({
        success: false,
        error: 'Укажите адрес доставки'
      });
    }

    const { data, error } = await supabase
      .from('orders')
      .insert([{
        customer_name: customer_name.trim(),
        phone: phone.trim(),
        product_name: product_name.trim(),
        category: category.trim(),
        price: price || null,
        size,
        quantity: parseInt(quantity) || 1,
        delivery_type,
        address: address ? address.trim() : null,
        comment: comment ? comment.trim() : null,
        source,
        status: 'new'
      }])
      .select('id')
      .single();

    if (error) {
      console.error('Supabase insert error:', error);
      return res.status(500).json({ success: false, error: 'Ошибка базы данных' });
    }

    return res.status(201).json({ success: true, id: data.id });
  }

  // ── GET: список заказов (для админки) ────────────────────────────────────
  if (req.method === 'GET') {
    const authHeader = req.headers['authorization'] || '';
    const token = authHeader.replace('Bearer ', '');

    if (token !== process.env.ADMIN_TOKEN) {
      return res.status(401).json({ success: false, error: 'Нет доступа' });
    }

    const { data, error } = await supabase
      .from('orders')
      .select('*')
      .order('created_at', { ascending: false })
      .limit(200);

    if (error) {
      return res.status(500).json({ success: false, error: 'Ошибка базы данных' });
    }

    return res.status(200).json({ success: true, orders: data });
  }

  return res.status(405).json({ error: 'Метод не поддерживается' });
};
