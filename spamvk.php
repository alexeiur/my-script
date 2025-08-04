<?php
/* Конфигурация */
const VK_API_VERSION = "5.207";
const VK_API_TOKEN   = "vk1.a.obZppS-NR6-lZyFZl4Gnq9s2oSvCPjpCBqMZTl__w4FYk9FdgLM7sr8Uas-Q46mgauVFHkVJ3ICWA1GaqoRDslWr3PP38cPa1CoGmKnDh2SUton9EYf18N79nNEDmtl1B4UfdAhQ07WnklHgk4SPmqjGZ1LCl9WcVJqIX5thD0XvUOdFfSloEZETzPbQwOwYCjs1WPUGDPqYhauYi0LhZQ"; // Токен с правами: friends,groups,wall,manage
const DELAY          = 3;   // Задержка между операциями (секунды)
const POST_TEXT      = "Добавь меня в друзья🚀";

// Список групп для постинга (указать ID с минусом)
const TARGET_GROUPS = [
    -64758790,  // Пример ID группы 1
    -34985835,  // Пример ID группы 2
    -39130136   // Пример ID группы 3
];

/**
 * Упрощенный запрос к VK API
 */
function vkRequest(string $method, array $params = []): array {
    $params['v'] = VK_API_VERSION;
    $params['access_token'] = VK_API_TOKEN;
    
    $response = file_get_contents(
        "https://api.vk.com/method/$method?" . http_build_query($params),
        false,
        stream_context_create([
            'http' => ['timeout' => 10],
            'ssl'  => ['verify_peer' => false]
        ])
    );
    
    return json_decode($response, true)['response'] ?? [];
}

/**
 * Основной цикл работы бота
 */
function runBot(): void {
    while (true) {
        try {
            // 1. Вечный онлайн
            vkRequest('account.setOnline');
            
            // 2. Автопринятие заявок в друзья
            $requests = vkRequest('friends.getRequests', ['need_viewed' => 1]);
            foreach ($requests['items'] ?? [] as $userId) {
                vkRequest('friends.add', ['user_id' => $userId]);
                sleep(DELAY);
            }
            
            // 3. Очистка неактивных друзей
            $friends = vkRequest('friends.get', ['fields' => 'last_seen']);
            foreach ($friends['items'] ?? [] as $friend) {
                if (!empty($friend['last_seen']['time'])) {
                    $inactiveDays = (time() - $friend['last_seen']['time']) / 86400;
                    if ($inactiveDays > 30) {
                        vkRequest('friends.delete', ['user_id' => $friend['id']]);
                        sleep(DELAY);
                    }
                }
            }
            
            // 4. Постинг в указанные группы
            foreach (TARGET_GROUPS as $groupId) {
                try {
                    vkRequest('wall.post', [
                        'owner_id' => $groupId,
                        'message' => POST_TEXT
                    ]);
                    echo "Posted to group $groupId\n";
                    sleep(DELAY * 2); // Увеличенная задержка для постинга
                } catch (Exception $e) {
                    echo "Error posting to $groupId: " . $e->getMessage() . "\n";
                }
            }
            
            // 5. Пауза между циклами (1 час)
            sleep(3600);
            
        } catch (Exception $e) {
            sleep(60); // При ошибке ждем минуту
        }
    }
}

// Запуск
if (PHP_SAPI === 'cli') {
    runBot();
} else {
    die('Скрипт предназначен только для CLI');
}