# Analisador de logs em Python

Ferramenta de terminal para contar registros por nível e identificar linhas inválidas em um arquivo de log. Usa apenas a biblioteca padrão do Python.

## Executar

Requer Python 3.10 ou superior. Na pasta do projeto:

```bash
python log_analyzer.py examples/app.log
```

Saída do exemplo:

```text
Linhas válidas: 7
Linhas inválidas: 1
DEBUG: 1
INFO: 2
WARNING: 1
ERROR: 2
CRITICAL: 1
```

Para analisar outro arquivo, passe o caminho como argumento. Use aspas quando houver espaços.

## Formato aceito

```text
2026-11-03 09:00:00 ERROR Falha ao conectar ao banco
```

- Data e hora precisam ser válidas, com precisão de segundos.
- Níveis aceitos: `DEBUG`, `INFO`, `WARNING`, `ERROR` e `CRITICAL`, em maiúsculas.
- A mensagem é obrigatória e pode conter espaços.
- Linhas em branco são ignoradas; outros registros fora do formato contam como inválidos.
- O arquivo deve estar em UTF-8. Falhas de leitura encerram o programa com código 2; uma análise concluída retorna 0, mesmo com linhas inválidas.

## Testes

```bash
python -m unittest discover -s tests -v
```

Os testes cobrem contagem, datas inválidas, registros incompletos, arquivo vazio, codificação e execução pela linha de comando. O GitHub Actions executa a mesma suíte a cada push e pull request.

## Organização

`parse_level` valida cada registro, `analyze` acumula as contagens e `main` cuida dos argumentos e da saída. A leitura percorre o arquivo linha por linha, sem carregar tudo na memória. A análise também aceita um iterador, permitindo testá-la sem arquivos reais.

O escopo é um formato de log de uma linha por evento. JSON, timestamps com fuso e stack traces de várias linhas ficam fora desta versão.
