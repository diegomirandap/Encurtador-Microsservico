## Descrição Geral do Projeto

Este projeto implementa um sistema de encurtamento de URLs usando Flask e PostgreSQL. O sistema é dividido em três componentes principais:

### Componentes do Sistema

1. **Banco de Dados (PostgreSQL)**: Armazena URLs encurtadas com informações como URL original, código curto, proprietário e estatísticas.

2. **Serviço Encurtador (porta 5000)**: Cria e gerencia URLs encurtadas, oferecendo endpoints para criação, consulta, exclusão e listagem de URLs.

3. **Serviço Redirecionador (porta 5001)**: Redireciona usuários das URLs curtas para as originais.

## Endpoints Adicionados

- `DELETE /api/v1/short-urls/{short_code}`: Deletar URL
- `GET /api/v1/admin/urls`: Listar todas as URLs (Como não foi implementado controle de acesso, estamos partindo do pressuposto que há um controle de usuários que possuem permissão de admin)
- `GET /api/v1/user/urls`: Listar URLs do usuário

## Melhoras Arquiteturais Futuras

### 1. Desempenho

**Situação Atual**: Banco único pode ser gargalo em alta carga.

**Melhorias**:
- Adicionar cache (Redis) para URLs frequentes
- Usar load balancing para múltiplas instâncias
- Otimizar consultas com índices no banco

### 2. Consistência de Dados

**Situação Atual**: Consistência básica via transações SQL.

**Melhorias**:
- Separar operações de leitura e escrita
- Implementar validação robusta de dados
- Adicionar backups automáticos

### 3. Acoplamento da Solução

**Situação Atual**: Serviços compartilham o mesmo banco e mesmo script, criando dependência.

**Melhorias**:
- Cada serviço com seu próprio banco
- Usar API Gateway para comunicação
- Implementar comunicação assíncrona com message brokers

### 4. Resiliência

**Situação Atual**: Pontos únicos de falha nos serviços.

**Melhorias**:
- Adicionar circuit breakers para prevenir falhas em cascata
- Implementar health checks e retry mechanisms
- Usar container orchestration (Kubernetes) para auto-healing
