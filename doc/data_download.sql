CREATE DATABASE `crawler` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';

-- @Table   crawler_download_info
-- @Desc    用于记录每条媒体资源基本信息以及爬取&下载状态
-- @Date    24.07.18
-- @Author  AInoriex
-- DROP TABLE IF EXISTS `crawler_download_info`;
CREATE TABLE `crawler_download_info` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '自增唯一ID',
    `vid` varchar(255) NOT NULL COMMENT '资源ID',
    `position` tinyint DEFAULT NULL COMMENT '1: cas, 2: cuhk, 3: quwan',
    `source_type` tinyint NOT NULL COMMENT '1: Bilibili, 2: 喜马拉雅, 3: YouTube',
    `source_link` text COMMENT '资源原始链接',
    `duration` int DEFAULT NULL COMMENT '原始长度(秒)',
    `cloud_type` tinyint DEFAULT NULL COMMENT '1: cos, 2: obs',
    `cloud_path` varchar(255) DEFAULT NULL COMMENT '云存储的路径',
    `language` varchar(10) DEFAULT NULL COMMENT '视频主要语言',
    `status` tinyint DEFAULT '0' COMMENT '0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传',
    `lock` tinyint DEFAULT '0' COMMENT '处理锁',
    `info` json DEFAULT NULL COMMENT 'meta数据',
    `comment` text COMMENT '备注',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
    `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
    PRIMARY KEY (`id`),
    UNIQUE KEY `vid` (`vid`),
    KEY `index_0` (`status`, `lock`),
    KEY `index_1` (`status`, `language`, `lock`),
    KEY `index_2` (`status`, `cloud_type`, `cloud_path`),
    KEY `index_3` (`language`, `status`, `lock`),
    KEY `index_4` (`source_type`, `status`, `lock`),
    KEY `index_5` (`source_type`, `language`, `status`, `lock`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = '爬虫数据采集记录表';