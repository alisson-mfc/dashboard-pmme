// api/dados.js - Serverless Function para servir dados de forma segura
export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Cache-Control', 's-maxage=3600, stale-while-revalidate');

  // Suporte a OPTIONS para CORS preflight
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }

  try {
    const dadosUrl = process.env.DADOS_URL;
    const githubToken = process.env.GITHUB_TOKEN;

    // Verificar configuração
    if (!dadosUrl) {
      console.error('DADOS_URL não configurado');
      return res.status(500).json({
        error: 'Configuração incompleta',
        message: 'DADOS_URL não configurado nas variáveis de ambiente'
      });
    }

    // Preparar headers para GitHub (se for repositório privado)
    const headers = {
      'Accept': 'application/json',
      'User-Agent': 'Vercel-Dashboard-PMMe'
    };

    if (githubToken) {
      headers['Authorization'] = `token ${githubToken}`;
    }

    // Buscar dados do GitHub
    console.log(`Buscando dados de: ${dadosUrl}`);
    const response = await fetch(dadosUrl, { headers });

    if (!response.ok) {
      console.error(`Erro ao buscar dados: ${response.status} ${response.statusText}`);

      if (response.status === 401 || response.status === 403) {
        return res.status(500).json({
          error: 'Erro de autenticação',
          message: 'Verifique se GITHUB_TOKEN está configurado corretamente'
        });
      }

      return res.status(500).json({
        error: 'Erro ao buscar dados',
        message: `GitHub retornou status ${response.status}`
      });
    }

    // Parse e retornar dados
    const dados = await response.json();
    console.log('Dados carregados com sucesso');

    res.status(200).json(dados);

  } catch (error) {
    console.error('Erro ao processar dados:', error.message);
    res.status(500).json({
      error: 'Erro ao carregar dados',
      message: error.message
    });
  }
}
