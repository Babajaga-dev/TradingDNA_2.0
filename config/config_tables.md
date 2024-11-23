# Configurazione TradingDNA 2.0 in Formato Tabellare

## 1. Configurazione Network

### Exchange Settings
| Parametro | Valore | Descrizione |
|-----------|---------|-------------|
| Nome | binance | Exchange utilizzato |
| Testnet | true | Modalità test attiva |
| API Key | "" | Da configurare via env |
| API Secret | "" | Da configurare via env |

### Connection Settings
| Parametro | Valore | Note |
|-----------|---------|-------|
| Timeout | 10000 | Millisecondi |
| Max Retries | 3 | Tentativi massimi |
| Retry Delay | 1000 | Millisecondi |
| Keepalive | true | Mantieni connessione |

### Rate Limits
| Parametro | Valore |
|-----------|---------|
| Max Requests/Min | 1200 |
| Max Orders/Sec | 10 |
| Max Positions | 50 |

### Trading Pairs
| Simbolo | Timeframes | Min Qty | Price Precision | Qty Precision |
|---------|------------|---------|-----------------|---------------|
| BTC/USDT | 1m,5m,15m,1h,4h,1d | 0.0001 | 2 | 8 |
| ETH/USDT | 1m,5m,15m,1h,4h,1d | 0.001 | 2 | 8 |

### WebSocket Settings
| Parametro | Valore |
|-----------|---------|
| Enabled | true |
| Buffer Size | 1000 |
| Max Reconnects | 5 |
| Channels | trades, klines, book |

## 2. Configurazione Trace (Logging)

### Global Settings
| Parametro | Valore |
|-----------|---------|
| Log Level | INFO |
| Format | %(asctime)s - %(name)s - %(levelname)s - %(message)s |
| Date Format | %Y-%m-%d %H:%M:%S |
| Encoding | utf-8 |

### File Settings
| Parametro | Valore | Note |
|-----------|---------|-------|
| Enabled | true | |
| Max Size | 400 KB | Per file |
| Total Max Size | 50 MB | Directory logs |
| Backup Count | 5 | |
| Retention Days | 30 | |
| Auto Clean | true | |
| Compress After | 7 giorni | |

### Visual Components
| Sistema | Icona | Colore |
|---------|--------|---------|
| DNA | 🧬 | blue |
| Immune | 🛡️ | green |
| Metabolism | ⚡ | yellow |
| Nervous | 🧠 | cyan |
| Endocrine | ⚖️ | magenta |
| Reproductive | 🔄 | blue |

### Alert Settings
| Livello | Email | Telegram |
|---------|--------|----------|
| Critical | ✓ | ✓ |
| Error | ✗ | ✓ |
| Warning | ✗ | ✗ |

### Metrics Collection
| Metrica | Intervallo | Note |
|---------|------------|------|
| Log Counts | 3600s | Reset contatori ogni ora |
| Storage | 900s | Check ogni 15 min |
| Performance | 300s | CPU, Memory, Disk, Latency |
| Errors | - | MTTF, MTTR |

## 3. Configurazione DNA

### General Settings
| Parametro | Valore |
|-----------|---------|
| Name | TradingDNA 2.0 |
| Version | 2.0.0 |

### Data Split Ratios
| Dataset | Ratio |
|---------|--------|
| Training | 0.7 |
| Validation | 0.15 |
| Testing | 0.15 |

### Pattern Recognition
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| Min Pattern Length | 5 | 3-10 |
| Max Pattern Length | 20 | 15-30 |
| Min Confidence | 0.7 | 0.5-0.9 |
| Similarity Threshold | 0.8 | 0.6-0.95 |
| Correlation Weight | 0.4 | 0.2-0.6 |
| Length Weight | 0.2 | 0.1-0.4 |
| Quality Threshold | 0.6 | 0.4-0.8 |

### Indicators Settings
#### RSI
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| Period | 14 | 5-30 |
| Overbought | 70 | 60-85 |
| Oversold | 30 | 15-40 |
| Signal Threshold | 0.6 | 0.3-0.9 |
| Weight | 1.0 | - |

#### MACD
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| Fast Period | 12 | 5-20 |
| Slow Period | 26 | 15-40 |
| Signal Period | 9 | 5-15 |
| Signal Threshold | 0.6 | 0.3-0.9 |
| Weight | 1.0 | - |

#### Bollinger Bands
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| Period | 20 | 10-30 |
| Num STD | 2.0 | 1.5-3.0 |
| Signal Threshold | 0.8 | 0.3-0.9 |
| Weight | 1.0 | - |

#### Volume
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| VWAP Period | 14 | 5-30 |
| Volume MA Period | 20 | 10-40 |
| Signal Threshold | 0.6 | 0.3-0.9 |
| Weight | 1.0 | - |

#### Strong Signal
| Parametro | Valore | Range Ottimizzazione |
|-----------|---------|---------------------|
| Window Size | 5 | 3-10 |
| Trend Threshold | 0.001 | 0.0005-0.002 |
| Signal Multiplier | 100.0 | 50.0-150.0 |
| Weight | 1.0 | 0.5-1.5 |

### Strategy Evolution
| Parametro | Valore |
|-----------|---------|
| Population Size | 100 |
| Generations | 50 |
| Mutation Rate | 0.1 |
| Crossover Rate | 0.8 |

### Validation Criteria
| Parametro | Valore |
|-----------|---------|
| Min Trades | 100 |
| Min Win Rate | 0.55 |
| Min Profit Factor | 1.5 |
| Max Drawdown | 0.2 |

### Signal Filters
| Filtro | Enabled | Parametri |
|--------|----------|-----------|
| Volatility | ✓ | Min ATR: 0.01, Max ATR: 0.05 |
| Volume | ✓ | Min Volume: 1,000,000 |
| Trend | ✓ | Lookback: 20 periodi |

### Backtest Settings
| Parametro | Valore | Note |
|-----------|---------|-------|
| Engine | vectorized | |
| Commission | 0.001 | 0.1% |
| Slippage | 0.0005 | 0.05% |
| Save Trades | ✓ | |
| Plot Equity | ✓ | |

### Metriche Report
- Sharpe Ratio
- Sortino Ratio
- Max Drawdown
- Win Rate
- Profit Factor