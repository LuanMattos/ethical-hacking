# Advanced Scanner - Scanning Methods Documentation

---

## 🇧🇷 PORTUGUÊS

### Como o Scanner Funciona

O Advanced Scanner utiliza **TCP Connect Scan** para detectar portas abertas em máquinas alvo.

#### 🔍 Método: TCP Connect Scan

```python
sock = socket(AF_INET, SOCK_STREAM)  # TCP (não ICMP)
sock.settimeout(1)
sock.connect((tgtHost, tgtPort))
```

**Especificações Técnicas:**
- **Protocolo**: TCP (Transmission Control Protocol)
- **AF_INET**: IPv4
- **SOCK_STREAM**: Streaming TCP
- **Timeout**: 1 segundo por porta

#### 📊 Como Detecta Portas

| Estado | O que ocorre | Resultado |
|--------|-------------|-----------|
| **ABERTA** | connect() sucede (handshake TCP) | Porta marcada como ABERTA ✓ |
| **FECHADA** | connect() falha (connection refused) | Porta marcada como FECHADA ✗ |
| **FILTRADA** | Timeout (firewall bloqueia) | Sem resposta |

#### Comparação com Outros Métodos

| Método | Protocolo | Velocidade | Confiabilidade | Stealth | Requer Admin |
|--------|-----------|-----------|-----------------|---------|--------------|
| **TCP Connect** | TCP | Lento | Alta | Não | Não |
| **SYN Stealth** | TCP | Médio | Alta | Sim | Sim* |
| **ICMP Ping** | ICMP | Muito Rápido | Média | Não | Não |
| **UDP Scan** | UDP | Lento | Baixa | Não | Não |
| **FIN/NULL** | TCP | Lento | Baixa | Sim | Sim* |

**\*Em Windows/Linux requer privilégios elevados*

#### ✅ Vantagens do TCP Connect

- Funciona em qualquer máquina (sem privilégios especiais)
- Muito confiável e preciso
- Funciona através de firewalls (na maioria dos casos)
- Compatível com todas as plataformas
- Fácil de implementar

#### ❌ Desvantagens do TCP Connect

- Deixa logs no servidor alvo (não é stealth)
- Mais lento (timeout de 1 segundo por porta)
- Gera muito tráfego de rede
- Pode ser detectado por IDS/IPS
- Requer conexão de rede lenta

#### 🎯 Quando Usar TCP Connect

- Varreduras legais e autorizadas
- Descoberta de serviços em redes corporativas
- Testes de penetração com permissão
- Avaliação de segurança de infraestrutura

---

## 🇬🇧 ENGLISH

### How the Scanner Works

The Advanced Scanner uses **TCP Connect Scan** to detect open ports on target machines.

#### 🔍 Method: TCP Connect Scan

```python
sock = socket(AF_INET, SOCK_STREAM)  # TCP (not ICMP)
sock.settimeout(1)
sock.connect((tgtHost, tgtPort))
```

**Technical Specifications:**
- **Protocol**: TCP (Transmission Control Protocol)
- **AF_INET**: IPv4
- **SOCK_STREAM**: TCP Streaming
- **Timeout**: 1 second per port

#### 📊 How It Detects Ports

| State | What Happens | Result |
|-------|--------------|--------|
| **OPEN** | connect() succeeds (TCP handshake) | Port marked as OPEN ✓ |
| **CLOSED** | connect() fails (connection refused) | Port marked as CLOSED ✗ |
| **FILTERED** | Timeout (firewall blocks) | No response |

#### Comparison with Other Methods

| Method | Protocol | Speed | Reliability | Stealth | Requires Admin |
|--------|----------|-------|-------------|---------|----------------|
| **TCP Connect** | TCP | Slow | High | No | No |
| **SYN Stealth** | TCP | Medium | High | Yes | Yes* |
| **ICMP Ping** | ICMP | Very Fast | Medium | No | No |
| **UDP Scan** | UDP | Slow | Low | No | No |
| **FIN/NULL** | TCP | Slow | Low | Yes | Yes* |

**\*On Windows/Linux requires elevated privileges*

#### ✅ Advantages of TCP Connect

- Works on any machine (no special privileges needed)
- Very reliable and accurate
- Works through firewalls (in most cases)
- Compatible with all platforms
- Easy to implement

#### ❌ Disadvantages of TCP Connect

- Leaves logs on target server (not stealth)
- Slower (1 second timeout per port)
- Generates significant network traffic
- Can be detected by IDS/IPS
- Slow on networks with high latency

#### 🎯 When to Use TCP Connect

- Legal and authorized scans
- Service discovery on corporate networks
- Penetration testing with permission
- Security infrastructure assessment

---

## 🇷🇺 РУССКИЙ

### Как работает сканер

Advanced Scanner использует **TCP Connect Scan** для обнаружения открытых портов на целевых машинах.

#### 🔍 Метод: TCP Connect Scan

```python
sock = socket(AF_INET, SOCK_STREAM)  # TCP (не ICMP)
sock.settimeout(1)
sock.connect((tgtHost, tgtPort))
```

**Технические характеристики:**
- **Протокол**: TCP (Transmission Control Protocol)
- **AF_INET**: IPv4
- **SOCK_STREAM**: TCP потоковая передача
- **Таймаут**: 1 секунда на порт

#### 📊 Как он обнаруживает порты

| Состояние | Что происходит | Результат |
|-----------|---------------|-----------|
| **ОТКРЫТ** | connect() успешен (3-way handshake TCP) | Порт отмечен как ОТКРЫТ ✓ |
| **ЗАКРЫТ** | connect() не удается (соединение отклонено) | Порт отмечен как ЗАКРЫТ ✗ |
| **ФИЛЬТРУЕТСЯ** | Таймаут (брандмауэр блокирует) | Нет ответа |

#### Сравнение с другими методами

| Метод | Протокол | Скорость | Надежность | Скрытность | Требует Admin |
|-------|----------|----------|-----------|-----------|---------------|
| **TCP Connect** | TCP | Медленно | Высокая | Нет | Нет |
| **SYN Stealth** | TCP | Средняя | Высокая | Да | Да* |
| **ICMP Ping** | ICMP | Очень быстро | Средняя | Нет | Нет |
| **UDP Scan** | UDP | Медленно | Низкая | Нет | Нет |
| **FIN/NULL** | TCP | Медленно | Низкая | Да | Да* |

**\*В Windows/Linux требуются повышенные привилегии*

#### ✅ Преимущества TCP Connect

- Работает на любой машине (не требует специальных привилегий)
- Очень надежен и точен
- Работает через брандмауэры (в большинстве случаев)
- Совместим со всеми платформами
- Легко реализуется

#### ❌ Недостатки TCP Connect

- Оставляет логи на целевом сервере (не скрытен)
- Медленнее (таймаут 1 секунда на порт)
- Генерирует значительный сетевой трафик
- Может быть обнаружен IDS/IPS
- Медленно работает при высокой задержке сети

#### 🎯 Когда использовать TCP Connect

- Легальные и авторизованные сканирования
- Обнаружение сервисов в корпоративных сетях
- Тестирование на проникновение с разрешением
- Оценка безопасности инфраструктуры

---

## 📚 Additional Resources / Дополнительные ресурсы / Дополнительные материалы

### Protocol Comparison Reference

**TCP Handshake (3-Way Handshake):**
1. Client sends SYN packet
2. Server responds with SYN-ACK
3. Client sends ACK

**In TCP Connect Scan:**
- ✅ All 3 steps complete = PORT OPEN
- ❌ Steps fail = PORT CLOSED

### Common Port Ranges

- **Well-known ports**: 0-1023 (requires admin on Unix)
- **Registered ports**: 1024-49151
- **Dynamic/Private**: 49152-65535

### Security Implications

⚠️ **Legal Notice**: Port scanning should only be performed:
- On systems you own
- With explicit written permission
- For authorized security testing
- In compliance with local laws

---

**Last Updated**: 2026-03-04  
**Scanner Version**: Advanced Scanner 1.0  
**Languages**: Portuguese 🇧🇷 | English 🇬🇧 | Russian 🇷🇺
