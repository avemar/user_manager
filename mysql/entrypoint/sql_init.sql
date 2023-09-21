CREATE SCHEMA IF NOT EXISTS `user_manager`;

CREATE TABLE IF NOT EXISTS `user_manager`.`users` (
    `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(255) NOT NULL,
    `email` VARCHAR(255) NOT NULL,
    `status` ENUM('ACTIVE', 'DISABLED') NOT NULL DEFAULT 'ACTIVE',
    `password` BINARY(64) NOT NULL,
    `salt` BINARY(64) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_modified` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    `last_login` DATETIME,
    PRIMARY KEY (`id`),
    UNIQUE KEY `users__email_idx` (`email`),
    KEY `users__status` (`status`),
    KEY `users__name` (`name`),
    KEY `users__created_at_idx` (`created_at`),
    KEY `users__last_modified_idx` (`last_modified`),
    KEY `users__last_login_idx` (`last_login`)
)  ENGINE=INNODB DEFAULT CHARSET=UTF8;

GRANT USAGE ON *.* TO 'BE_user_manager'@'%';
DROP USER 'BE_user_manager'@'%';
CREATE USER 'BE_user_manager'@'%' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE ON `user_manager`.* TO 'BE_user_manager'@'%';
FLUSH PRIVILEGES;

