# Blockmesh Bot


---

## ⚙️ Install & Run

```bash
git clone https://github.com/Hoanghienvi/Blockmesh-Network.git
```

```bash
cd Blockmesh-Network
screen -S blockmesh
python3 -m venv venv
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```
```bash
nano account.txt
```

```bash
python main.py
```

---

## 📂 Files

- `main.py` → Main bot script
- `account.txt` → Add accounts in `email:password` format (one per line)
- `proxies.txt` → Optional, use `http://user:pass@host:port` (one per line)

---

## 🌐 Proxy Usage

The script will ask:

```
Use proxies? (y/n)
```

- `y` → Uses all proxies in parallel
- `n` → Uses your direct internet connection

---
