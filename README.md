# ⏱️ Simulação do Algoritmo de Berkeley

Este projeto simula o algoritmo de Berkeley para sincronização de relógios em sistemas distribuídos, utilizando Python e sockets.

## 📋 Descrição

O algoritmo de Berkeley é utilizado para sincronizar relógios em sistemas distribuídos sem a necessidade de um relógio de referência externo. Neste projeto, um processo atua como coordenador, solicitando os tempos dos clientes e calculando a média para ajustar todos os relógios.

## 🚀 Tecnologias Utilizadas

- Python 3.11
- Sockets
- Threading

## 🛠️ Instalação e Execução

1. **Clone o repositório:**

   ```bash
   git clone https://github.com/seuusuario/clocky-synchronization.git
   cd clocky-synchronization
   
## Como Executar

### Coordenador
Execute em um terminal:
```bash
python process_berkeley.py P0 coordinator
```

### Clientes
Execute **em terminais separados** (1 por cliente):
```bash
python process_berkeley.py P1 client
python process_berkeley.py P2 client
python process_berkeley.py P3 client
python process_berkeley.py P4 client
```

## 🔧 Funcionamento
1. O coordenador aguarda **4 clientes** se conectarem.  
2. Solicita o tempo atual de cada cliente.  
3. Calcula a média dos tempos recebidos.  
4. Envia um ajuste (em segundos) para cada cliente sincronizar seu relógio.  
5. Clientes exibem:  
   - Tempo antes do ajuste (`Local Time`).  
   - Tempo após ajuste (`Adjusted Time`).  

## ✅ Requisitos
- **Clientes**: 4 instâncias (IDs de 1 a 4).  
- **Diferença inicial**: ±10 segundos entre relógios.  
- **Precisão pós-sincronização**: Diferença < 1 segundo.
  
## 👥 Desenvolvedores
- **José Vinicius Cavalcante Soares** - 22112113  
- **Liedson da Silva Santos** - 22110823  
- **Thalia de Oliveira Santos** - 21110245

## 📜 Licença
MIT License - Consulte [LICENSE](LICENSE) para detalhes.
