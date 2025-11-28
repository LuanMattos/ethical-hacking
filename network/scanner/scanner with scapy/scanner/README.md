# Visualizador de Protocolos de Rede

Pequeno projeto em Python 3 que usa Scapy para capturar pacotes e uma interface Tkinter + matplotlib para mostrar, em tempo real, as contagens dos protocolos/layers observados.

Avisos importantes
- A captura de pacotes normalmente requer privilégios elevados (sudo no Linux/macOS ou executar o terminal como Administrador no Windows com Npcap instalado). Use apenas em redes que você possui ou tem permissão.
- Teste em um ambiente controlado.

Requisitos
- Python 3.8+
- scapy
- matplotlib
- (opcional) tk já vem com a maioria das distribuições Python

Instalação
```
python3 -m pip install -r requirements.txt
```

Uso
```
# Executando a partir da pasta raiz do projeto (onde está a pasta scanner):
cd scanner
sudo python3 -m src.main        # no Linux/macOS, captura na interface padrão
sudo python3 -m src.main -i eth0
sudo python3 -m src.main -f "port 53"
```

O que faz
- Inicia um AsyncSniffer do Scapy que incrementa contadores por camada/protocolo visto em cada pacote.
- Mostra um gráfico de barras (matplotlib embutido em Tkinter) com contagens por camada.
- Controles: Iniciar/Parar captura e Limpar contadores.

Melhorias possíveis
- Exportar logs (JSON/CSV), série temporal por protocolo, detalhes por pacote ao clicar, UI mais rica com PyQt ou web (Dash/Plotly), empacotar em executável, etc.