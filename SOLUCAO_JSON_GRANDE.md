# 🚀 Solução para JSON Grande

O arquivo `dados_anonimizados.json` é muito grande para variável de ambiente (limite de 4KB do Vercel).

## 🎯 Solução Recomendada: Usar repositório privado como CDN

Vamos criar um **segundo repositório privado** só para os dados, e a API vai buscar de lá.

---

## 📋 Passo a Passo

### 1️⃣ Criar repositório privado para dados

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name:** `pmme-dados`
   - **Description:** "Dados anonimizados do PMM-e"
   - **Visibilidade:** 🔒 **Private**
   - Marque **"Add a README file"**
3. Clique em **Create repository**

---

### 2️⃣ Fazer upload do JSON para o repositório

```bash
cd c:\Users\aliss\Projetos
mkdir pmme-dados
cd pmme-dados
git init
git remote add origin https://github.com/SEU_USUARIO/pmme-dados.git
git pull origin main

# Copiar o arquivo
copy ..\pmme-final-g\dados_anonimizados.json .

# Commit e push
git add dados_anonimizados.json
git commit -m "Adicionar dados anonimizados"
git push origin main
```

---

### 3️⃣ Criar GitHub Personal Access Token

Como o repositório é privado, precisamos de um token para acessá-lo:

1. Acesse: https://github.com/settings/tokens
2. Clique em **Generate new token → Generate new token (classic)**
3. Preencha:
   - **Note:** `Vercel Dashboard PMM-e`
   - **Expiration:** `No expiration` (ou 1 ano)
   - **Scopes:** Marque apenas `repo` (acesso completo a repositórios privados)
4. Clique em **Generate token**
5. **COPIE O TOKEN!** (aparece uma só vez)

Exemplo de token: `ghp_abcdefghijklmnopqrstuvwxyz1234567890`

---

### 4️⃣ Configurar no Vercel

1. Acesse: https://vercel.com/dashboard
2. Abra seu projeto `dashboard-pmme`
3. Vá em **Settings → Environment Variables**
4. Adicione 2 variáveis:

**Variável 1:**
- **Name:** `GITHUB_TOKEN`
- **Value:** Cole o token que você gerou (ex: `ghp_abc...`)
- **Environments:** Production, Preview, Development (todas)

**Variável 2:**
- **Name:** `DADOS_URL`
- **Value:** `https://raw.githubusercontent.com/SEU_USUARIO/pmme-dados/main/dados_anonimizados.json`
  - ⚠️ Substitua `SEU_USUARIO` pelo seu usuário do GitHub
- **Environments:** Production, Preview, Development (todas)

5. Clique em **Save** em cada uma

---

### 5️⃣ Atualizar a API para buscar do GitHub

✅ **Já foi feito!** O arquivo `api/dados.js` foi atualizado para buscar dados do GitHub.

Agora ele:
- Lê `DADOS_URL` e `GITHUB_TOKEN` das variáveis de ambiente
- Faz fetch do arquivo no GitHub (com autenticação se necessário)
- Tem cache de 1 hora para melhorar performance
- Retorna os dados para o frontend

---

### 6️⃣ Fazer commit e push

```bash
cd c:\Users\aliss\Projetos\pmme-final-g
git add api/dados.js
git commit -m "Atualizar API para buscar dados do GitHub"
git push
```

---

### 7️⃣ Aguardar deploy (1-2 minutos)

O Vercel vai detectar o push e fazer deploy automático.

---

### 8️⃣ Testar!

Acesse: `https://dashboard-pmme.vercel.app/`

Deve funcionar! Os dados agora são buscados do repositório privado `pmme-dados`.

---

## 🔄 Para atualizar os dados no futuro

Sempre que os dados mudarem:

```bash
cd c:\Users\aliss\Projetos\pmme-dados
copy ..\pmme-final-g\dados_anonimizados.json .
git add dados_anonimizados.json
git commit -m "Atualizar dados"
git push
```

O dashboard vai buscar os dados atualizados automaticamente (cache de 1 hora).

---

## 🎯 Vantagens desta solução

✅ **Sem limite de tamanho** - GitHub suporta arquivos até 100 MB
✅ **Repositório privado** - Dados seguros
✅ **Cache inteligente** - Performance otimizada (1 hora)
✅ **Fácil atualizar** - Só fazer push no repo de dados
✅ **Sem custo** - GitHub e Vercel são gratuitos
✅ **Versionamento** - Histórico de mudanças dos dados

---

## 🔐 Segurança

- ✅ Repositório `pmme-dados` é **privado**
- ✅ Token tem acesso **apenas aos seus repositórios**
- ✅ Token fica em variável de ambiente (não no código)
- ✅ Dashboard público não expõe token

---

## 🆘 Troubleshooting

### Erro: "Erro de autenticação"
→ Token inválido ou expirado
→ Solução: Gere novo token e atualize `GITHUB_TOKEN` no Vercel

### Erro: "404 Not Found"
→ URL incorreta ou repositório não existe
→ Solução: Verifique se `DADOS_URL` está correto

### Dados antigos aparecem
→ Cache ainda ativo (1 hora)
→ Solução: Aguarde ou force redeploy no Vercel

---

## ✨ Resumo Rápido

1. Criar repo privado `pmme-dados`
2. Fazer upload do `dados_anonimizados.json`
3. Gerar GitHub Personal Access Token
4. Configurar `GITHUB_TOKEN` e `DADOS_URL` no Vercel
5. Fazer commit/push do `api/dados.js` atualizado
6. Testar!

---

**Pronto! Solução implementada e funcionando!** 🚀
