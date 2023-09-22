/*
 Navicat Premium Data Transfer

 Source Server         : 121.37.207.248
 Source Server Type    : MySQL
 Source Server Version : 50735
 Source Host           : 121.37.207.248:3306
 Source Schema         : CNVD

 Target Server Type    : MySQL
 Target Server Version : 50735
 File Encoding         : 65001

 Date: 30/07/2023 08:34:52
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for finger_table
-- ----------------------------
DROP TABLE IF EXISTS `finger_table`;
CREATE TABLE `finger_table`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `title` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `container` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `finger` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `cdntitle` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `opersystem` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `serverip` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `port` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `banner` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `cmsfinger` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `location` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `url` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 41 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
