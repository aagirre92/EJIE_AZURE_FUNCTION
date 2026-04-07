## EJIE Azure Function

This project is a timer-triggered Azure Function that monitors EJIE public job postings.

On each run, it:
- Opens the EJIE listings page
- Detects open offers
- Reads each offer detail page and extracts the main information
- Sends a formatted notification to a Telegram chat

If something fails, it logs the error and sends an alert message to Telegram.

Required environment variables: `TIMER_SCHEDULE`, `BASE_URL`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.

## Flow

EJIE is the Basque Government IT organization (Sociedad Informatica del Gobierno Vasco). This function watches its public jobs board and only processes open postings.

### Quick Flow

```mermaid
flowchart LR
	A[Timer runs] --> B[Read EJIE job listings]
	B --> C[Keep only open positions]
	C --> D[Open each position detail]
	D --> E[Extract key data]
	E --> F[Send Telegram alert]
	F --> G[End]
```

### Detailed Flow

```mermaid
flowchart TD
	A[Timer trigger] --> B[Build EJIE empleo_publico URL]
	B --> C[GET listings page]
	C --> D[Parse HTML and find li.r01srItem]
	D --> E{Has class marker r01srItemTypo_empleo_publico_abierto?}
	E -- No --> N[Skip item]
	E -- Yes --> F[Read offer link from em.r01srItemDocName a]
	F --> G[GET offer detail page]
	G --> H[Extract fields into DataFrame]
	H --> I[Format Telegram HTML message]
	I --> J[Send Telegram notification]
	J --> K{More items?}
	N --> K
	K -- Yes --> E
	K -- No --> L[Log execution finished]

	C -. exception .-> X[Catch exception]
	D -. exception .-> X
	G -. exception .-> X
	J -. exception .-> X
	X --> Y[Log error + send Telegram alert]
```
