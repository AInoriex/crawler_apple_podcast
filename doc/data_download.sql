CREATE DATABASE `crawler` CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_general_ci';

-- @Table   crawler_apple_podcast
-- @Desc    用于记录每条媒体资源基本信息以及爬取&下载状态
-- @Date    24.05.24
-- @Author  Xyh
CREATE TABLE `crawler_apple_podcast` (
    `id` int NOT NULL AUTO_INCREMENT COMMENT '自增唯一ID',
    `vid` varchar(255) NOT NULL COMMENT '视频ID',
    `path` text COMMENT '本地路径',
    `position` tinyint DEFAULT NULL COMMENT '1: cas, 2: cuhk, 3: quwan',
    `cloud_path` text COMMENT '云存储的路径',
    `result_path` text COMMENT '处理结果路径',
    `type` tinyint NOT NULL COMMENT '1: Bilibili, 2: 喜马拉雅, 3: YouTube',
    `duration` int DEFAULT NULL COMMENT '原始长度',
    `valid_duration` int DEFAULT NULL COMMENT '有效长度',
    `valid_segement` int DEFAULT NULL COMMENT '有效片段数',
    `link` varchar(255) DEFAULT NULL COMMENT '完整视频链接',
    `language` varchar(10) DEFAULT NULL COMMENT '视频主要语言',
    `status` tinyint DEFAULT '0' COMMENT '0: 已爬取, 1: 本地已下载, 2: 已上传云端未处理, 3: 已处理未上传, 4: 已处理已上传',
    `lock` tinyint DEFAULT '0' COMMENT '处理锁',
    `info` json DEFAULT NULL COMMENT 'meta数据',
    `created_at` datetime DEFAULT CURRENT_TIMESTAMP COMMENT '数据创建时间',
    `updated_at` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '数据更新时间',
    `filtered_duration` int DEFAULT NULL COMMENT '过滤后的长度',
    `filtered_segement` int DEFAULT NULL COMMENT '过滤后的片段数',
    `filtered_idx` text COMMENT '过滤后的索引',
    PRIMARY KEY (`id`),
    UNIQUE KEY `vid` (`vid`),
    KEY `index_0` (`status`, `lock`),
    KEY `index_1` (`status`, `language`, `lock`),
    KEY `index_2` (`language`, `status`, `lock`),
    KEY `index_3` (`type`, `status`, `lock`),
    KEY `index_4` (`language`, `duration`, `valid_duration`),
    KEY `index_5` (`language`, `type`, `valid_duration`),
    KEY `index_6` (`type`, `language`, `status`, `lock`),
    KEY `index_7` (`type`, `language`, `status`, `valid_duration`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = 'ApplePodcast爬取记录表';