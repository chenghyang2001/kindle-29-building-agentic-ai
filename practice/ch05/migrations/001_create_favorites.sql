-- 收藏表：(user_id, product_id) 聯合唯一，資料庫層也擋重複收藏
-- 本演練實際用記憶體 Map 實作，這份 schema 是給換成真實資料庫時用的藍圖
CREATE TABLE IF NOT EXISTS favorites (
  user_id    INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  created_at TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id, product_id),
  FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_favorites_user ON favorites(user_id);

-- down
-- DROP TABLE IF EXISTS favorites;
