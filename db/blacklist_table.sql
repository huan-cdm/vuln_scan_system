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

 Date: 30/07/2023 08:34:11
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for blacklist_table
-- ----------------------------
DROP TABLE IF EXISTS `blacklist_table`;
CREATE TABLE `blacklist_table`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 508 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
