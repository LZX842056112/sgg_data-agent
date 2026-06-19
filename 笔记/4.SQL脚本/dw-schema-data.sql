/*
 Navicat Premium Data Transfer

 Source Server         : 192.168.200.10
 Source Server Type    : MySQL
 Source Server Version : 80045
 Source Host           : 192.168.200.10:3306
 Source Schema         : dw

 Target Server Type    : MySQL
 Target Server Version : 80045
 File Encoding         : 65001

 Date: 17/02/2026 12:48:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for dim_customer
-- ----------------------------
DROP TABLE IF EXISTS `dim_customer`;
CREATE TABLE `dim_customer`  (
  `customer_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `customer_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `member_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`customer_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of dim_customer
-- ----------------------------
INSERT INTO `dim_customer` VALUES ('C001', '李伟', '男', '黄金');
INSERT INTO `dim_customer` VALUES ('C002', '王芳', '女', '白银');
INSERT INTO `dim_customer` VALUES ('C003', '张敏', '女', '黄金');
INSERT INTO `dim_customer` VALUES ('C004', '刘洋', '男', '青铜');
INSERT INTO `dim_customer` VALUES ('C005', '陈静', '女', '铂金');
INSERT INTO `dim_customer` VALUES ('C006', '赵磊', '男', '白银');
INSERT INTO `dim_customer` VALUES ('C007', '黄秀英', '女', '青铜');
INSERT INTO `dim_customer` VALUES ('C008', '吴斌', '男', '黄金');
INSERT INTO `dim_customer` VALUES ('C009', '周燕', '女', '铂金');
INSERT INTO `dim_customer` VALUES ('C010', '徐浩', '男', '白银');
INSERT INTO `dim_customer` VALUES ('C011', '孙丽', '女', '黄金');
INSERT INTO `dim_customer` VALUES ('C012', '马强', '男', '青铜');
INSERT INTO `dim_customer` VALUES ('C013', '朱玲', '女', '白银');
INSERT INTO `dim_customer` VALUES ('C014', '胡杰', '男', '黄金');
INSERT INTO `dim_customer` VALUES ('C015', '高梅', '女', '铂金');
INSERT INTO `dim_customer` VALUES ('C016', '林峰', '男', '青铜');
INSERT INTO `dim_customer` VALUES ('C017', '何娜', '女', '白银');
INSERT INTO `dim_customer` VALUES ('C018', '郭涛', '男', '黄金');
INSERT INTO `dim_customer` VALUES ('C019', '邓慧', '女', '青铜');
INSERT INTO `dim_customer` VALUES ('C020', '曹瑞', '男', '铂金');

-- ----------------------------
-- Table structure for dim_date
-- ----------------------------
DROP TABLE IF EXISTS `dim_date`;
CREATE TABLE `dim_date`  (
  `date_id` int NOT NULL,
  `year` int NULL DEFAULT NULL,
  `quarter` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `month` int NULL DEFAULT NULL,
  `day` int NULL DEFAULT NULL,
  PRIMARY KEY (`date_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of dim_date
-- ----------------------------
INSERT INTO `dim_date` VALUES (20250101, 2025, 'Q1', 1, 1);
INSERT INTO `dim_date` VALUES (20250102, 2025, 'Q1', 1, 2);
INSERT INTO `dim_date` VALUES (20250103, 2025, 'Q1', 1, 3);
INSERT INTO `dim_date` VALUES (20250104, 2025, 'Q1', 1, 4);
INSERT INTO `dim_date` VALUES (20250105, 2025, 'Q1', 1, 5);
INSERT INTO `dim_date` VALUES (20250106, 2025, 'Q1', 1, 6);
INSERT INTO `dim_date` VALUES (20250107, 2025, 'Q1', 1, 7);
INSERT INTO `dim_date` VALUES (20250108, 2025, 'Q1', 1, 8);
INSERT INTO `dim_date` VALUES (20250109, 2025, 'Q1', 1, 9);
INSERT INTO `dim_date` VALUES (20250110, 2025, 'Q1', 1, 10);
INSERT INTO `dim_date` VALUES (20250111, 2025, 'Q1', 1, 11);
INSERT INTO `dim_date` VALUES (20250112, 2025, 'Q1', 1, 12);
INSERT INTO `dim_date` VALUES (20250113, 2025, 'Q1', 1, 13);
INSERT INTO `dim_date` VALUES (20250114, 2025, 'Q1', 1, 14);
INSERT INTO `dim_date` VALUES (20250115, 2025, 'Q1', 1, 15);
INSERT INTO `dim_date` VALUES (20250116, 2025, 'Q1', 1, 16);
INSERT INTO `dim_date` VALUES (20250117, 2025, 'Q1', 1, 17);
INSERT INTO `dim_date` VALUES (20250118, 2025, 'Q1', 1, 18);
INSERT INTO `dim_date` VALUES (20250119, 2025, 'Q1', 1, 19);
INSERT INTO `dim_date` VALUES (20250120, 2025, 'Q1', 1, 20);
INSERT INTO `dim_date` VALUES (20250121, 2025, 'Q1', 1, 21);
INSERT INTO `dim_date` VALUES (20250122, 2025, 'Q1', 1, 22);
INSERT INTO `dim_date` VALUES (20250123, 2025, 'Q1', 1, 23);
INSERT INTO `dim_date` VALUES (20250124, 2025, 'Q1', 1, 24);
INSERT INTO `dim_date` VALUES (20250125, 2025, 'Q1', 1, 25);
INSERT INTO `dim_date` VALUES (20250126, 2025, 'Q1', 1, 26);
INSERT INTO `dim_date` VALUES (20250127, 2025, 'Q1', 1, 27);
INSERT INTO `dim_date` VALUES (20250128, 2025, 'Q1', 1, 28);
INSERT INTO `dim_date` VALUES (20250129, 2025, 'Q1', 1, 29);
INSERT INTO `dim_date` VALUES (20250130, 2025, 'Q1', 1, 30);
INSERT INTO `dim_date` VALUES (20250131, 2025, 'Q1', 1, 31);
INSERT INTO `dim_date` VALUES (20250201, 2025, 'Q1', 2, 1);
INSERT INTO `dim_date` VALUES (20250202, 2025, 'Q1', 2, 2);
INSERT INTO `dim_date` VALUES (20250203, 2025, 'Q1', 2, 3);
INSERT INTO `dim_date` VALUES (20250204, 2025, 'Q1', 2, 4);
INSERT INTO `dim_date` VALUES (20250205, 2025, 'Q1', 2, 5);
INSERT INTO `dim_date` VALUES (20250206, 2025, 'Q1', 2, 6);
INSERT INTO `dim_date` VALUES (20250207, 2025, 'Q1', 2, 7);
INSERT INTO `dim_date` VALUES (20250208, 2025, 'Q1', 2, 8);
INSERT INTO `dim_date` VALUES (20250209, 2025, 'Q1', 2, 9);
INSERT INTO `dim_date` VALUES (20250210, 2025, 'Q1', 2, 10);
INSERT INTO `dim_date` VALUES (20250211, 2025, 'Q1', 2, 11);
INSERT INTO `dim_date` VALUES (20250212, 2025, 'Q1', 2, 12);
INSERT INTO `dim_date` VALUES (20250213, 2025, 'Q1', 2, 13);
INSERT INTO `dim_date` VALUES (20250214, 2025, 'Q1', 2, 14);
INSERT INTO `dim_date` VALUES (20250215, 2025, 'Q1', 2, 15);
INSERT INTO `dim_date` VALUES (20250216, 2025, 'Q1', 2, 16);
INSERT INTO `dim_date` VALUES (20250217, 2025, 'Q1', 2, 17);
INSERT INTO `dim_date` VALUES (20250218, 2025, 'Q1', 2, 18);
INSERT INTO `dim_date` VALUES (20250219, 2025, 'Q1', 2, 19);
INSERT INTO `dim_date` VALUES (20250220, 2025, 'Q1', 2, 20);
INSERT INTO `dim_date` VALUES (20250221, 2025, 'Q1', 2, 21);
INSERT INTO `dim_date` VALUES (20250222, 2025, 'Q1', 2, 22);
INSERT INTO `dim_date` VALUES (20250223, 2025, 'Q1', 2, 23);
INSERT INTO `dim_date` VALUES (20250224, 2025, 'Q1', 2, 24);
INSERT INTO `dim_date` VALUES (20250225, 2025, 'Q1', 2, 25);
INSERT INTO `dim_date` VALUES (20250226, 2025, 'Q1', 2, 26);
INSERT INTO `dim_date` VALUES (20250227, 2025, 'Q1', 2, 27);
INSERT INTO `dim_date` VALUES (20250228, 2025, 'Q1', 2, 28);
INSERT INTO `dim_date` VALUES (20250301, 2025, 'Q1', 3, 1);
INSERT INTO `dim_date` VALUES (20250302, 2025, 'Q1', 3, 2);
INSERT INTO `dim_date` VALUES (20250303, 2025, 'Q1', 3, 3);
INSERT INTO `dim_date` VALUES (20250304, 2025, 'Q1', 3, 4);
INSERT INTO `dim_date` VALUES (20250305, 2025, 'Q1', 3, 5);
INSERT INTO `dim_date` VALUES (20250306, 2025, 'Q1', 3, 6);
INSERT INTO `dim_date` VALUES (20250307, 2025, 'Q1', 3, 7);
INSERT INTO `dim_date` VALUES (20250308, 2025, 'Q1', 3, 8);
INSERT INTO `dim_date` VALUES (20250309, 2025, 'Q1', 3, 9);
INSERT INTO `dim_date` VALUES (20250310, 2025, 'Q1', 3, 10);
INSERT INTO `dim_date` VALUES (20250311, 2025, 'Q1', 3, 11);
INSERT INTO `dim_date` VALUES (20250312, 2025, 'Q1', 3, 12);
INSERT INTO `dim_date` VALUES (20250313, 2025, 'Q1', 3, 13);
INSERT INTO `dim_date` VALUES (20250314, 2025, 'Q1', 3, 14);
INSERT INTO `dim_date` VALUES (20250315, 2025, 'Q1', 3, 15);
INSERT INTO `dim_date` VALUES (20250316, 2025, 'Q1', 3, 16);
INSERT INTO `dim_date` VALUES (20250317, 2025, 'Q1', 3, 17);
INSERT INTO `dim_date` VALUES (20250318, 2025, 'Q1', 3, 18);
INSERT INTO `dim_date` VALUES (20250319, 2025, 'Q1', 3, 19);
INSERT INTO `dim_date` VALUES (20250320, 2025, 'Q1', 3, 20);
INSERT INTO `dim_date` VALUES (20250321, 2025, 'Q1', 3, 21);
INSERT INTO `dim_date` VALUES (20250322, 2025, 'Q1', 3, 22);
INSERT INTO `dim_date` VALUES (20250323, 2025, 'Q1', 3, 23);
INSERT INTO `dim_date` VALUES (20250324, 2025, 'Q1', 3, 24);
INSERT INTO `dim_date` VALUES (20250325, 2025, 'Q1', 3, 25);
INSERT INTO `dim_date` VALUES (20250326, 2025, 'Q1', 3, 26);
INSERT INTO `dim_date` VALUES (20250327, 2025, 'Q1', 3, 27);
INSERT INTO `dim_date` VALUES (20250328, 2025, 'Q1', 3, 28);
INSERT INTO `dim_date` VALUES (20250329, 2025, 'Q1', 3, 29);
INSERT INTO `dim_date` VALUES (20250330, 2025, 'Q1', 3, 30);
INSERT INTO `dim_date` VALUES (20250331, 2025, 'Q1', 3, 31);

-- ----------------------------
-- Table structure for dim_product
-- ----------------------------
DROP TABLE IF EXISTS `dim_product`;
CREATE TABLE `dim_product`  (
  `product_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `product_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `brand` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`product_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of dim_product
-- ----------------------------
INSERT INTO `dim_product` VALUES ('P001', 'iPhone 15 Pro', '手机数码', '苹果');
INSERT INTO `dim_product` VALUES ('P002', 'Galaxy S24 Ultra', '手机数码', '三星');
INSERT INTO `dim_product` VALUES ('P003', 'Mate 60 Pro', '手机数码', '华为');
INSERT INTO `dim_product` VALUES ('P004', '戴森 V15 吸尘器', '家用电器', '戴森');
INSERT INTO `dim_product` VALUES ('P005', '美的空调 KFR-35GW', '家用电器', '美的');
INSERT INTO `dim_product` VALUES ('P006', '耐克 Air Max 270 运动鞋', '鞋靴', '耐克');
INSERT INTO `dim_product` VALUES ('P007', '阿迪达斯 Ultraboost 跑鞋', '鞋靴', '阿迪达斯');
INSERT INTO `dim_product` VALUES ('P008', '优衣库 Heattech 保暖夹克', '服饰', '优衣库');
INSERT INTO `dim_product` VALUES ('P009', '李维斯 501 牛仔裤', '服饰', '李维斯');
INSERT INTO `dim_product` VALUES ('P010', '雀巢金牌速溶咖啡', '食品饮料', '雀巢');
INSERT INTO `dim_product` VALUES ('P011', '蒙牛纯牛奶 250ml*12', '食品饮料', '蒙牛');
INSERT INTO `dim_product` VALUES ('P012', '乐事原味薯片 150g', '休闲零食', '乐事');
INSERT INTO `dim_product` VALUES ('P013', '奥利奥巧克力夹心饼干', '休闲零食', '奥利奥');
INSERT INTO `dim_product` VALUES ('P014', 'Kindle Paperwhite 电子书', '手机数码', '亚马逊');
INSERT INTO `dim_product` VALUES ('P015', 'Instant Pot 多功能电压力锅', '家用电器', 'Instant Pot');

-- ----------------------------
-- Table structure for dim_region
-- ----------------------------
DROP TABLE IF EXISTS `dim_region`;
CREATE TABLE `dim_region`  (
  `region_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `province` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `region_name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `country` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`region_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of dim_region
-- ----------------------------
INSERT INTO `dim_region` VALUES ('R001', '广东省', '华南', '中国');
INSERT INTO `dim_region` VALUES ('R002', '浙江省', '华东', '中国');
INSERT INTO `dim_region` VALUES ('R003', '四川省', '西南', '中国');
INSERT INTO `dim_region` VALUES ('R004', '北京市', '华北', '中国');
INSERT INTO `dim_region` VALUES ('R005', '上海市', '华东', '中国');
INSERT INTO `dim_region` VALUES ('R006', '湖北省', '华中', '中国');

-- ----------------------------
-- Table structure for fact_order
-- ----------------------------
DROP TABLE IF EXISTS `fact_order`;
CREATE TABLE `fact_order`  (
  `order_id` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `customer_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `product_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `date_id` int NULL DEFAULT NULL,
  `region_id` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `order_quantity` int NULL DEFAULT NULL,
  `order_amount` float NULL DEFAULT NULL,
  PRIMARY KEY (`order_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of fact_order
-- ----------------------------
INSERT INTO `fact_order` VALUES ('ORD20250101001', 'C001', 'P001', 20250101, 'R001', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250101002', 'C005', 'P003', 20250101, 'R005', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250102001', 'C003', 'P010', 20250102, 'R002', 5, 125);
INSERT INTO `fact_order` VALUES ('ORD20250102002', 'C008', 'P006', 20250102, 'R004', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250103001', 'C012', 'P011', 20250103, 'R003', 12, 60);
INSERT INTO `fact_order` VALUES ('ORD20250103002', 'C015', 'P014', 20250103, 'R005', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250104001', 'C002', 'P012', 20250104, 'R001', 8, 40);
INSERT INTO `fact_order` VALUES ('ORD20250105001', 'C007', 'P008', 20250105, 'R006', 2, 299);
INSERT INTO `fact_order` VALUES ('ORD20250105002', 'C010', 'P010', 20250105, 'R002', 8, 200);
INSERT INTO `fact_order` VALUES ('ORD20250106001', 'C010', 'P002', 20250106, 'R002', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250107001', 'C019', 'P013', 20250107, 'R003', 10, 35);
INSERT INTO `fact_order` VALUES ('ORD20250108001', 'C004', 'P005', 20250108, 'R001', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250108002', 'C016', 'P005', 20250108, 'R001', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250109001', 'C011', 'P009', 20250109, 'R004', 1, 599);
INSERT INTO `fact_order` VALUES ('ORD20250110001', 'C006', 'P007', 20250110, 'R005', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250110002', 'C003', 'P010', 20250110, 'R002', 5, 125);
INSERT INTO `fact_order` VALUES ('ORD20250111001', 'C013', 'P004', 20250111, 'R002', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250112001', 'C017', 'P015', 20250112, 'R006', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250113001', 'C020', 'P001', 20250113, 'R005', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250114001', 'C009', 'P010', 20250114, 'R004', 3, 75);
INSERT INTO `fact_order` VALUES ('ORD20250115001', 'C014', 'P003', 20250115, 'R001', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250116001', 'C001', 'P012', 20250116, 'R001', 6, 30);
INSERT INTO `fact_order` VALUES ('ORD20250117001', 'C005', 'P006', 20250117, 'R005', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250118001', 'C003', 'P011', 20250118, 'R002', 10, 50);
INSERT INTO `fact_order` VALUES ('ORD20250119001', 'C008', 'P014', 20250119, 'R004', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250120001', 'C012', 'P008', 20250120, 'R003', 1, 199);
INSERT INTO `fact_order` VALUES ('ORD20250120002', 'C014', 'P013', 20250120, 'R001', 25, 87.5);
INSERT INTO `fact_order` VALUES ('ORD20250121001', 'C015', 'P002', 20250121, 'R005', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250122001', 'C002', 'P013', 20250122, 'R001', 12, 42);
INSERT INTO `fact_order` VALUES ('ORD20250123001', 'C007', 'P005', 20250123, 'R006', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250124001', 'C010', 'P009', 20250124, 'R002', 2, 1198);
INSERT INTO `fact_order` VALUES ('ORD20250125001', 'C019', 'P007', 20250125, 'R003', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250125002', 'C018', 'P001', 20250125, 'R003', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250126001', 'C004', 'P004', 20250126, 'R001', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250127001', 'C011', 'P015', 20250127, 'R004', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250128001', 'C006', 'P001', 20250128, 'R005', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250129001', 'C013', 'P010', 20250129, 'R002', 4, 100);
INSERT INTO `fact_order` VALUES ('ORD20250130001', 'C017', 'P003', 20250130, 'R006', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250130002', 'C009', 'P010', 20250130, 'R004', 6, 150);
INSERT INTO `fact_order` VALUES ('ORD20250131001', 'C020', 'P012', 20250131, 'R005', 7, 35);
INSERT INTO `fact_order` VALUES ('ORD20250201001', 'C009', 'P011', 20250201, 'R004', 8, 40);
INSERT INTO `fact_order` VALUES ('ORD20250202001', 'C014', 'P006', 20250202, 'R001', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250203001', 'C001', 'P014', 20250203, 'R001', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250204001', 'C005', 'P008', 20250204, 'R005', 1, 199);
INSERT INTO `fact_order` VALUES ('ORD20250205001', 'C003', 'P002', 20250205, 'R002', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250205002', 'C008', 'P012', 20250205, 'R004', 12, 60);
INSERT INTO `fact_order` VALUES ('ORD20250206001', 'C008', 'P013', 20250206, 'R004', 9, 31.5);
INSERT INTO `fact_order` VALUES ('ORD20250207001', 'C012', 'P005', 20250207, 'R003', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250208001', 'C015', 'P009', 20250208, 'R005', 1, 599);
INSERT INTO `fact_order` VALUES ('ORD20250209001', 'C002', 'P007', 20250209, 'R001', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250210001', 'C007', 'P004', 20250210, 'R006', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250210002', 'C019', 'P011', 20250210, 'R003', 20, 100);
INSERT INTO `fact_order` VALUES ('ORD20250211001', 'C010', 'P015', 20250211, 'R002', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250212001', 'C019', 'P001', 20250212, 'R003', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250213001', 'C004', 'P010', 20250213, 'R001', 6, 150);
INSERT INTO `fact_order` VALUES ('ORD20250214001', 'C011', 'P003', 20250214, 'R004', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250215001', 'C006', 'P012', 20250215, 'R005', 10, 50);
INSERT INTO `fact_order` VALUES ('ORD20250215002', 'C016', 'P003', 20250215, 'R001', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250216001', 'C013', 'P011', 20250216, 'R002', 15, 75);
INSERT INTO `fact_order` VALUES ('ORD20250217001', 'C017', 'P006', 20250217, 'R006', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250218001', 'C020', 'P014', 20250218, 'R005', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250219001', 'C009', 'P008', 20250219, 'R004', 2, 398);
INSERT INTO `fact_order` VALUES ('ORD20250220001', 'C014', 'P002', 20250220, 'R001', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250220002', 'C006', 'P012', 20250220, 'R005', 18, 90);
INSERT INTO `fact_order` VALUES ('ORD20250221001', 'C001', 'P013', 20250221, 'R001', 11, 38.5);
INSERT INTO `fact_order` VALUES ('ORD20250222001', 'C005', 'P005', 20250222, 'R005', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250223001', 'C003', 'P009', 20250223, 'R002', 1, 599);
INSERT INTO `fact_order` VALUES ('ORD20250224001', 'C008', 'P007', 20250224, 'R004', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250225001', 'C012', 'P004', 20250225, 'R003', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250226001', 'C015', 'P015', 20250226, 'R005', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250227001', 'C002', 'P001', 20250227, 'R001', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250228001', 'C007', 'P010', 20250228, 'R006', 5, 125);
INSERT INTO `fact_order` VALUES ('ORD20250228002', 'C004', 'P012', 20250228, 'R001', 14, 70);
INSERT INTO `fact_order` VALUES ('ORD20250301001', 'C010', 'P003', 20250301, 'R002', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250301002', 'C017', 'P011', 20250301, 'R006', 30, 150);
INSERT INTO `fact_order` VALUES ('ORD20250302001', 'C019', 'P012', 20250302, 'R003', 9, 45);
INSERT INTO `fact_order` VALUES ('ORD20250303001', 'C004', 'P011', 20250303, 'R001', 10, 50);
INSERT INTO `fact_order` VALUES ('ORD20250304001', 'C011', 'P006', 20250304, 'R004', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250305001', 'C006', 'P014', 20250305, 'R005', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250305002', 'C007', 'P012', 20250305, 'R006', 20, 100);
INSERT INTO `fact_order` VALUES ('ORD20250306001', 'C013', 'P008', 20250306, 'R002', 1, 199);
INSERT INTO `fact_order` VALUES ('ORD20250307001', 'C017', 'P002', 20250307, 'R006', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250308001', 'C020', 'P013', 20250308, 'R005', 14, 49);
INSERT INTO `fact_order` VALUES ('ORD20250309001', 'C009', 'P005', 20250309, 'R004', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250310001', 'C014', 'P009', 20250310, 'R001', 1, 599);
INSERT INTO `fact_order` VALUES ('ORD20250310002', 'C013', 'P011', 20250310, 'R002', 20, 100);
INSERT INTO `fact_order` VALUES ('ORD20250311001', 'C001', 'P007', 20250311, 'R001', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250312001', 'C005', 'P004', 20250312, 'R005', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250312002', 'C012', 'P011', 20250312, 'R003', 24, 120);
INSERT INTO `fact_order` VALUES ('ORD20250313001', 'C003', 'P015', 20250313, 'R002', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250314001', 'C008', 'P001', 20250314, 'R004', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250315001', 'C012', 'P010', 20250315, 'R003', 7, 175);
INSERT INTO `fact_order` VALUES ('ORD20250315002', 'C020', 'P013', 20250315, 'R005', 22, 77);
INSERT INTO `fact_order` VALUES ('ORD20250316001', 'C015', 'P003', 20250316, 'R005', 1, 6999);
INSERT INTO `fact_order` VALUES ('ORD20250317001', 'C002', 'P012', 20250317, 'R001', 12, 60);
INSERT INTO `fact_order` VALUES ('ORD20250318001', 'C007', 'P011', 20250318, 'R006', 18, 90);
INSERT INTO `fact_order` VALUES ('ORD20250318002', 'C015', 'P013', 20250318, 'R005', 30, 105);
INSERT INTO `fact_order` VALUES ('ORD20250319001', 'C010', 'P006', 20250319, 'R002', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250320001', 'C019', 'P014', 20250320, 'R003', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250320002', 'C018', 'P014', 20250320, 'R003', 1, 1399);
INSERT INTO `fact_order` VALUES ('ORD20250321001', 'C004', 'P008', 20250321, 'R001', 3, 597);
INSERT INTO `fact_order` VALUES ('ORD20250322001', 'C011', 'P002', 20250322, 'R004', 1, 9499);
INSERT INTO `fact_order` VALUES ('ORD20250322002', 'C011', 'P011', 20250322, 'R004', 16, 80);
INSERT INTO `fact_order` VALUES ('ORD20250323001', 'C006', 'P013', 20250323, 'R005', 16, 56);
INSERT INTO `fact_order` VALUES ('ORD20250324001', 'C013', 'P005', 20250324, 'R002', 1, 3200);
INSERT INTO `fact_order` VALUES ('ORD20250325001', 'C017', 'P009', 20250325, 'R006', 2, 1198);
INSERT INTO `fact_order` VALUES ('ORD20250325002', 'C002', 'P010', 20250325, 'R001', 10, 250);
INSERT INTO `fact_order` VALUES ('ORD20250326001', 'C020', 'P007', 20250326, 'R005', 1, 1299);
INSERT INTO `fact_order` VALUES ('ORD20250327001', 'C009', 'P004', 20250327, 'R004', 1, 5499);
INSERT INTO `fact_order` VALUES ('ORD20250328001', 'C014', 'P015', 20250328, 'R001', 1, 899);
INSERT INTO `fact_order` VALUES ('ORD20250329001', 'C001', 'P001', 20250329, 'R001', 1, 8999);
INSERT INTO `fact_order` VALUES ('ORD20250329002', 'C005', 'P013', 20250329, 'R005', 18, 63);
INSERT INTO `fact_order` VALUES ('ORD20250330001', 'C005', 'P010', 20250330, 'R005', 4, 100);
INSERT INTO `fact_order` VALUES ('ORD20250330002', 'C008', 'P012', 20250330, 'R004', 15, 75);
INSERT INTO `fact_order` VALUES ('ORD20250331001', 'C003', 'P003', 20250331, 'R002', 1, 6999);

SET FOREIGN_KEY_CHECKS = 1;
