Frequência máxima de operação: 
<img width="289" height="32" alt="image" src="https://github.com/user-attachments/assets/62fdfe10-564f-4ef6-bd81-bfedc44073ea" />



Pior caminho:
<img width="927" height="138" alt="image" src="https://github.com/user-attachments/assets/63000c84-5d4b-4f4e-9d2c-b13adf9fb6d1" />

Pior caminho detalhado:
<img width="703" height="307" alt="image" src="https://github.com/user-attachments/assets/48e81549-618b-42ae-b025-bfc3f9ca3f42" />
<img width="649" height="245" alt="image" src="https://github.com/user-attachments/assets/4133c7a0-c8bc-4430-ace2-addab46f2f8f" />
<img width="805" height="281" alt="image" src="https://github.com/user-attachments/assets/27bcbcea-38c6-4c25-a92b-69cd8183e9f9" />

O pior caminho crítico começa no registrador do contador de programa (`pc[8]`) e termina no banco de registradores (`R[29][21]`). Esse caminho passa pela memória de instruções (ROM), por circuitos combinacionais de seleção de dados, incluindo multiplexadores, e pela lógica de acesso à memória RAM.

Esse caminho limita a frequência máxima de operação porque o processador utiliza uma arquitetura *single-cycle*, na qual todas as operações de uma instrução precisam ser concluídas em um único ciclo de clock. Assim, o atraso acumulado dos componentes determina o período mínimo necessário para o clock e, consequentemente, a frequência máxima de funcionamento (Fmax).


Quantidade e percentual de LUTs utilizadas:
<img width="250" height="12" alt="image" src="https://github.com/user-attachments/assets/a36d854a-c5eb-4a3b-8df7-3a147d531e8e" />


Quantidade e percentual de memória interna utilizada:
<img width="251" height="10" alt="image" src="https://github.com/user-attachments/assets/21cd590e-fc42-4919-9fa1-ccc443734c1d" />

