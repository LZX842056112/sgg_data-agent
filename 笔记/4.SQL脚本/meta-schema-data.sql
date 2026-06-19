/*
 Navicat Premium Data Transfer

 Source Server         : 192.168.200.10
 Source Server Type    : MySQL
 Source Server Version : 80045
 Source Host           : 192.168.200.10:3306
 Source Schema         : meta

 Target Server Type    : MySQL
 Target Server Version : 80045
 File Encoding         : 65001

 Date: 17/02/2026 12:48:28
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for column_info
-- ----------------------------
DROP TABLE IF EXISTS `column_info`;
CREATE TABLE `column_info`  (
  `id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '列编号',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '列名称',
  `type` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '数据类型',
  `role` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '列类型(primary_key,foreign_key,measure,dimension)',
  `examples` json NULL COMMENT '数据示例',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '列描述',
  `alias` json NULL COMMENT '列别名',
  `table_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '所属表编号',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of column_info
-- ----------------------------
INSERT INTO `column_info` VALUES ('dim_customer.customer_id', 'customer_id', 'varchar(20)', 'primary_key', '[\"C001\", \"C002\", \"C003\", \"C004\", \"C005\", \"C006\", \"C007\", \"C008\", \"C009\", \"C010\"]', '客户唯一标识。', '[\"客户ID\", \"用户ID\"]', 'dim_customer');
INSERT INTO `column_info` VALUES ('dim_customer.customer_name', 'customer_name', 'varchar(50)', 'dimension', '[\"李伟\", \"王芳\", \"张敏\", \"刘洋\", \"陈静\", \"赵磊\", \"黄秀英\", \"吴斌\", \"周燕\", \"徐浩\"]', '客户名称。', '[\"客户名称\", \"用户名称\"]', 'dim_customer');
INSERT INTO `column_info` VALUES ('dim_customer.gender', 'gender', 'varchar(10)', 'dimension', '[\"男\", \"女\"]', '客户性别。', '[\"性别\"]', 'dim_customer');
INSERT INTO `column_info` VALUES ('dim_customer.member_level', 'member_level', 'varchar(20)', 'dimension', '[\"黄金\", \"白银\", \"青铜\", \"铂金\"]', '客户会员等级。', '[\"会员等级\", \"用户等级\"]', 'dim_customer');
INSERT INTO `column_info` VALUES ('dim_date.date_id', 'date_id', 'int', 'primary_key', '[20250101, 20250102, 20250103, 20250104, 20250105, 20250106, 20250107, 20250108, 20250109, 20250110]', '日期唯一标识，格式 yyyyMMdd。', '[\"日期ID\", \"日期\"]', 'dim_date');
INSERT INTO `column_info` VALUES ('dim_date.day', 'day', 'int', 'dimension', '[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]', '日。', '[\"日\", \"天\"]', 'dim_date');
INSERT INTO `column_info` VALUES ('dim_date.month', 'month', 'int', 'dimension', '[1, 2, 3]', '月份。', '[\"月\", \"月份\"]', 'dim_date');
INSERT INTO `column_info` VALUES ('dim_date.quarter', 'quarter', 'varchar(2)', 'dimension', '[\"Q1\"]', '季度。', '[\"季度\"]', 'dim_date');
INSERT INTO `column_info` VALUES ('dim_date.year', 'year', 'int', 'dimension', '[2025]', '年份。', '[\"年\", \"年份\"]', 'dim_date');
INSERT INTO `column_info` VALUES ('dim_product.brand', 'brand', 'varchar(50)', 'dimension', '[\"苹果\", \"三星\", \"华为\", \"戴森\", \"美的\", \"耐克\", \"阿迪达斯\", \"优衣库\", \"李维斯\", \"雀巢\"]', '商品品牌名称。', '[\"品牌\", \"品牌名称\"]', 'dim_product');
INSERT INTO `column_info` VALUES ('dim_product.category', 'category', 'varchar(50)', 'dimension', '[\"手机数码\", \"家用电器\", \"鞋靴\", \"服饰\", \"食品饮料\", \"休闲零食\"]', '商品所属品类。', '[\"商品类别\", \"品类\", \"分类\"]', 'dim_product');
INSERT INTO `column_info` VALUES ('dim_product.product_id', 'product_id', 'varchar(20)', 'primary_key', '[\"P001\", \"P002\", \"P003\", \"P004\", \"P005\", \"P006\", \"P007\", \"P008\", \"P009\", \"P010\"]', '商品唯一标识。', '[\"商品ID\", \"产品ID\"]', 'dim_product');
INSERT INTO `column_info` VALUES ('dim_product.product_name', 'product_name', 'varchar(200)', 'dimension', '[\"iPhone 15 Pro\", \"Galaxy S24 Ultra\", \"Mate 60 Pro\", \"戴森 V15 吸尘器\", \"美的空调 KFR-35GW\", \"耐克 Air Max 270 运动鞋\", \"阿迪达斯 Ultraboost 跑鞋\", \"优衣库 Heattech 保暖夹克\", \"李维斯 501 牛仔裤\", \"雀巢金牌速溶咖啡\"]', '商品名称。', '[\"商品名称\", \"产品名称\"]', 'dim_product');
INSERT INTO `column_info` VALUES ('dim_region.country', 'country', 'varchar(50)', 'dimension', '[\"中国\"]', '地区所属国家名称。', '[\"国家\", \"国家名称\"]', 'dim_region');
INSERT INTO `column_info` VALUES ('dim_region.province', 'province', 'varchar(50)', 'dimension', '[\"广东省\", \"浙江省\", \"四川省\", \"北京市\", \"上海市\", \"湖北省\"]', '订单所属的省份名称。', '[\"省份\", \"省\", \"所在省份\"]', 'dim_region');
INSERT INTO `column_info` VALUES ('dim_region.region_id', 'region_id', 'varchar(20)', 'primary_key', '[\"R001\", \"R002\", \"R003\", \"R004\", \"R005\", \"R006\"]', '地区唯一标识。', '[\"地区ID\", \"区域ID\"]', 'dim_region');
INSERT INTO `column_info` VALUES ('dim_region.region_name', 'region_name', 'varchar(50)', 'dimension', '[\"华南\", \"华东\", \"西南\", \"华北\", \"华中\"]', '订单所属的大区名称，如华东、华南等。', '[\"地区\", \"区域\", \"大区\"]', 'dim_region');
INSERT INTO `column_info` VALUES ('fact_order.customer_id', 'customer_id', 'varchar(20)', 'foreign_key', '[\"C001\", \"C005\", \"C003\", \"C008\", \"C012\", \"C015\", \"C002\", \"C007\", \"C010\", \"C019\"]', '关联客户维度的外键。', '[\"客户ID\", \"用户ID\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.date_id', 'date_id', 'int', 'foreign_key', '[20250101, 20250102, 20250103, 20250104, 20250105, 20250106, 20250107, 20250108, 20250109, 20250110]', '关联时间维度的外键。', '[\"日期\", \"下单日期\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.order_amount', 'order_amount', 'float', 'measure', '[8999.0, 6999.0, 125.0, 899.0, 60.0, 1399.0, 40.0, 299.0, 200.0, 9499.0]', '订单金额。', '[\"销售额\", \"订单金额\", \"收入\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.order_id', 'order_id', 'varchar(30)', 'primary_key', '[\"ORD20250101001\", \"ORD20250101002\", \"ORD20250102001\", \"ORD20250102002\", \"ORD20250103001\", \"ORD20250103002\", \"ORD20250104001\", \"ORD20250105001\", \"ORD20250105002\", \"ORD20250106001\"]', '订单唯一标识。', '[\"订单ID\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.order_quantity', 'order_quantity', 'int', 'measure', '[1, 5, 12, 8, 2, 10, 3, 6, 25, 4]', '订单中商品的购买数量。', '[\"销量\", \"购买数量\", \"件数\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.product_id', 'product_id', 'varchar(20)', 'foreign_key', '[\"P001\", \"P003\", \"P010\", \"P006\", \"P011\", \"P014\", \"P012\", \"P008\", \"P002\", \"P013\"]', '关联商品维度的外键。', '[\"商品ID\", \"产品ID\"]', 'fact_order');
INSERT INTO `column_info` VALUES ('fact_order.region_id', 'region_id', 'varchar(20)', 'foreign_key', '[\"R001\", \"R005\", \"R002\", \"R004\", \"R003\", \"R006\"]', '关联地区维度的外键。', '[\"地区ID\", \"区域ID\"]', 'fact_order');

-- ----------------------------
-- Table structure for column_metric
-- ----------------------------
DROP TABLE IF EXISTS `column_metric`;
CREATE TABLE `column_metric`  (
  `column_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '列编号',
  `metric_id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '指标编号',
  PRIMARY KEY (`column_id`, `metric_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of column_metric
-- ----------------------------
INSERT INTO `column_metric` VALUES ('fact_order.order_amount', 'GMV');
INSERT INTO `column_metric` VALUES ('fact_order.order_quantity', 'AOV');

-- ----------------------------
-- Table structure for metric_info
-- ----------------------------
DROP TABLE IF EXISTS `metric_info`;
CREATE TABLE `metric_info`  (
  `id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '指标编码',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '指标名称',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '指标描述',
  `relevant_columns` json NULL COMMENT '关联的列',
  `alias` json NULL COMMENT '指标别名',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of metric_info
-- ----------------------------
INSERT INTO `metric_info` VALUES ('AOV', 'AOV', '全称Average Order Value，表示所有订单的成交金额平均值。', '[\"fact_order.order_quantity\"]', '[\"平均单价\", \"平均订单金额\"]');
INSERT INTO `metric_info` VALUES ('GMV', 'GMV', '全称Gross Merchandise Value，表示所有订单的成交金额总和。', '[\"fact_order.order_amount\"]', '[\"成交总额\", \"订单总额\"]');

-- 1. 订单类核心指标
INSERT INTO metric_info (id, name, description, relevant_columns, alias)
VALUES
-- 订单数量类
('ORDER_COUNT', '订单总数', '统计周期内的订单总数量，按order_id去重计数。', '["fact_order.order_id"]', '["订单数", "下单量"]'),
('ORDER_COUNT_BY_REGION', '各区域订单数', '按地区维度（region_id/region_name）统计的订单数量。', '["fact_order.order_id", "dim_region.region_id", "dim_region.region_name"]', '["区域订单量", "各地区下单数"]'),
-- 销量类
('SALES_QUANTITY', '商品销售总量', '统计周期内所有订单的商品购买数量总和。', '["fact_order.order_quantity"]', '["总销量", "销售件数"]'),
('SALES_QUANTITY_BY_CATEGORY', '品类销量', '按商品品类（category）统计的商品销售数量。', '["fact_order.order_quantity", "dim_product.category"]', '["品类销售件数", "分类销量"]'),
-- 客单价/消费能力类
('AVG_ORDER_QUANTITY', '平均订单商品数', '订单商品购买数量的平均值（总销量/订单总数）。', '["fact_order.order_quantity", "fact_order.order_id"]', '["单均商品数", "平均购买件数"]'),
('AVG_AMOUNT_BY_CUSTOMER', '客户平均消费额', '统计周期内客户的平均订单金额（GMV/客户数）。', '["fact_order.order_amount", "fact_order.customer_id"]', '["客均消费", "客户平均下单金额"]'),
-- 会员等级相关
('GMV_BY_MEMBER_LEVEL', '各会员等级GMV', '按客户会员等级（member_level）统计的成交总额。', '["fact_order.order_amount", "dim_customer.member_level"]', '["会员等级销售额", "各等级成交总额"]'),
-- 时间维度类
('DAILY_GMV', '日成交总额', '按日期维度（date_id/year/month/day）统计的每日GMV。', '["fact_order.order_amount", "dim_date.date_id", "dim_date.year", "dim_date.month", "dim_date.day"]', '["日GMV", "每日成交总额"]'),
('QUARTERLY_SALES', '季度销量', '按季度（quarter）统计的商品销售总量。', '["fact_order.order_quantity", "dim_date.quarter"]', '["季度销售件数", "季度销量"]'),
-- 品牌/商品类
('GMV_BY_BRAND', '品牌成交总额', '按商品品牌（brand）统计的成交总额。', '["fact_order.order_amount", "dim_product.brand"]', '["品牌GMV", "各品牌销售额"]'),
('TOP_PRODUCT_SALES', '热销商品销量', '按商品名称（product_name）排序的商品销售数量TOP榜。', '["fact_order.order_quantity", "dim_product.product_id", "dim_product.product_name"]', '["商品销量TOP", "热销商品件数"]');

-- 2. 客户类分析指标
INSERT INTO metric_info (id, name, description, relevant_columns, alias)
VALUES
('CUSTOMER_COUNT', '客户总数', '统计周期内下单的客户总数量，按customer_id去重计数。', '["fact_order.customer_id"]', '["下单客户数", "客户数量"]'),
('CUSTOMER_COUNT_BY_GENDER', '各性别客户数', '按客户性别（gender）统计的下单客户数量。', '["fact_order.customer_id", "dim_customer.gender"]', '["性别客户数", "男女下单人数"]'),
('MEMBER_LEVEL_COUNT', '各会员等级客户数', '按会员等级（member_level）统计的下单客户数量。', '["fact_order.customer_id", "dim_customer.member_level"]', '["会员等级客户数", "各等级下单人数"]');




-- 关联订单类指标与对应列
INSERT INTO column_metric (column_id, metric_id)
VALUES
-- 订单数量类
('fact_order.order_id', 'ORDER_COUNT'),
('fact_order.order_id', 'ORDER_COUNT_BY_REGION'),
('dim_region.region_id', 'ORDER_COUNT_BY_REGION'),
-- 销量类
('fact_order.order_quantity', 'SALES_QUANTITY'),
('fact_order.order_quantity', 'SALES_QUANTITY_BY_CATEGORY'),
('dim_product.category', 'SALES_QUANTITY_BY_CATEGORY'),
-- 客单价/消费能力类
('fact_order.order_quantity', 'AVG_ORDER_QUANTITY'),
('fact_order.order_id', 'AVG_ORDER_QUANTITY'),
('fact_order.order_amount', 'AVG_AMOUNT_BY_CUSTOMER'),
('fact_order.customer_id', 'AVG_AMOUNT_BY_CUSTOMER'),
-- 会员等级相关
('fact_order.order_amount', 'GMV_BY_MEMBER_LEVEL'),
('dim_customer.member_level', 'GMV_BY_MEMBER_LEVEL'),
-- 时间维度类
('fact_order.order_amount', 'DAILY_GMV'),
('dim_date.date_id', 'DAILY_GMV'),
('fact_order.order_quantity', 'QUARTERLY_SALES'),
('dim_date.quarter', 'QUARTERLY_SALES'),
-- 品牌/商品类
('fact_order.order_amount', 'GMV_BY_BRAND'),
('dim_product.brand', 'GMV_BY_BRAND'),
('fact_order.order_quantity', 'TOP_PRODUCT_SALES'),
('dim_product.product_id', 'TOP_PRODUCT_SALES'),
-- 客户类
('fact_order.customer_id', 'CUSTOMER_COUNT'),
('fact_order.customer_id', 'CUSTOMER_COUNT_BY_GENDER'),
('dim_customer.gender', 'CUSTOMER_COUNT_BY_GENDER'),
('fact_order.customer_id', 'MEMBER_LEVEL_COUNT'),
('dim_customer.member_level', 'MEMBER_LEVEL_COUNT');
-- ----------------------------
-- Table structure for table_info
-- ----------------------------
DROP TABLE IF EXISTS `table_info`;
CREATE TABLE `table_info`  (
  `id` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL COMMENT '表编号',
  `name` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '表名称',
  `role` varchar(32) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL COMMENT '表类型(fact/dim)',
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL COMMENT '表描述',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of table_info
-- ----------------------------
INSERT INTO `table_info` VALUES ('dim_customer', 'dim_customer', 'dim', '客户维度表，描述下单客户的基本属性。');
INSERT INTO `table_info` VALUES ('dim_date', 'dim_date', 'dim', '时间维度表，用于多时间粒度分析。');
INSERT INTO `table_info` VALUES ('dim_product', 'dim_product', 'dim', '商品维度表，描述商品的基本属性信息。');
INSERT INTO `table_info` VALUES ('dim_region', 'dim_region', 'dim', '地区维度表，用于描述订单发生的地理区域信息。');
INSERT INTO `table_info` VALUES ('fact_order', 'fact_order', 'fact', '订单事实表，记录订单数量和金额等核心指标。');

SET FOREIGN_KEY_CHECKS = 1;
