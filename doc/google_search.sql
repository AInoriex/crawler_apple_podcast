-- @Table   web_search_info
-- @Desc    用于记录缓存Google搜索结果
CREATE TABLE `web_search_info` (
    `id` int(11) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `request_id` varchar(500) DEFAULT '' COMMENT '请求ID',
    `search_from` varchar(50) DEFAULT '' COMMENT '检索源',
    `search_keyword` varchar(100) DEFAULT '' COMMENT '检索关键字',
    `result_url` varchar(500) DEFAULT '' COMMENT '检索链接结果',
    `apple_podcast_user_id` varchar(64) DEFAULT '' COMMENT 'apple播客用户id',
    `crawl_status` tinyint(3) DEFAULT 0 COMMENT '处理状态 0初始化 1待处理 2处理中 3处理成功 4处理失败',
    `create_time` timestamp NULL DEFAULT NULL COMMENT '创建时间',
    `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_url` (`result_url`)
) ENGINE = InnoDB AUTO_INCREMENT = 1 DEFAULT CHARSET = utf8mb4 COMMENT = '检索信息记录表';