import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "./App.css";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = React.createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      // Verify token validity
      axios.get(`${API}/me`)
        .then(response => setUser(response.data))
        .catch(() => {
          localStorage.removeItem('token');
          setToken(null);
          setUser(null);
        });
    }
  }, [token]);

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/login`, { username, password });
      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      setUser({ username: response.data.username });
      return true;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  const register = async (username, password) => {
    try {
      const response = await axios.post(`${API}/register`, { username, password });
      const newToken = response.data.access_token;
      setToken(newToken);
      localStorage.setItem('token', newToken);
      axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
      setUser({ username: response.data.username });
      return true;
    } catch (error) {
      console.error('Register error:', error);
      return false;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

// Header Component
const Header = () => {
  const { user, logout } = React.useContext(AuthContext);

  return (
    <header className="header">
      <div className="header-content">
        <Link to="/" className="logo-link">
          <img 
            src="https://upload.wikimedia.org/wikipedia/commons/2/2b/Bandeira_do_estado_de_S%C3%A3o_Paulo.svg" 
            alt="Bandeira de São Paulo" 
            className="logo"
          />
          <h1 className="site-title">BRIGADA PAULISTA</h1>
        </Link>
        
        <nav className="nav-links">
          <Link to="/" className="nav-link">Início</Link>
          <Link to="/forum" className="nav-link">Fórum</Link>
          <a href="https://t.me/brigadapaulista" target="_blank" rel="noopener noreferrer" className="nav-link telegram-link">
            📱 Telegram
          </a>
          
          {user ? (
            <div className="user-menu">
              <span className="username">Bem-vindo, {user.username}</span>
              <button onClick={logout} className="logout-btn">Sair</button>
            </div>
          ) : (
            <Link to="/auth" className="nav-link auth-link">Entrar</Link>
          )}
        </nav>
      </div>
    </header>
  );
};

// Home Page
const HomePage = () => {
  return (
    <div className="home-page">
      <div className="hero-section">
        <div className="hero-content">
          <h2 className="hero-title">Por São Paulo Livre e Independente!</h2>
          <p className="hero-subtitle">
            A Brigada Paulista é o movimento sucessor legítimo dos grandes movimentos separatistas paulistas do passado.
          </p>
          <div className="hero-buttons">
            <Link to="/forum" className="btn btn-primary">Acesse o Fórum</Link>
            <a href="https://t.me/brigadapaulista" target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
              Junte-se no Telegram
            </a>
          </div>
        </div>
      </div>

      <div className="content-section">
        <div className="history-section">
          <h3>Nossa História</h3>
          <div className="history-timeline">
            <div className="timeline-item">
              <div className="year">1887</div>
              <div className="content">
                <h4>Separatismo Paulista de 1887</h4>
                <p>
                  O primeiro grande movimento separatista paulista surge no final do Império, 
                  liderado pelas elites cafeicultoras e setores republicanos, descontentes com 
                  a centralização imperial e as mudanças nas políticas escravistas.
                </p>
              </div>
            </div>
            
            <div className="timeline-item">
              <div className="year">1932</div>
              <div className="content">
                <h4>Revolução Constitucionalista de 1932</h4>
                <p>
                  O maior levante paulista da história! São Paulo se ergue contra a ditadura 
                  de Getúlio Vargas, mobilizando toda a população em defesa da autonomia paulista 
                  e da democracia constitucional. A data de 9 de julho marca para sempre 
                  o espírito de resistência paulista.
                </p>
              </div>
            </div>
            
            <div className="timeline-item current">
              <div className="year">2025</div>
              <div className="content">
                <h4>Brigada Paulista - O Renascimento</h4>
                <p>
                  A Brigada Paulista surge como o movimento sucessor legítimo desses 
                  grandes levantes do passado. Defendemos a independência total de São Paulo, 
                  nossa autonomia econômica e o direito do povo paulista à autodeterminação.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="manifesto-section">
          <h3>Nossos Ideais</h3>
          <div className="ideals-grid">
            <div className="ideal-card">
              <h4>🏛️ Autonomia Política</h4>
              <p>São Paulo livre para tomar suas próprias decisões políticas e administrativas.</p>
            </div>
            <div className="ideal-card">
              <h4>💰 Independência Econômica</h4>
              <p>Nossos recursos e riquezas devem servir primeiro ao povo paulista.</p>
            </div>
            <div className="ideal-card">
              <h4>🎯 Autodeterminação</h4>
              <p>O direito fundamental do povo paulista de decidir seu próprio destino.</p>
            </div>
            <div className="ideal-card">
              <h4>🚀 Progresso e Desenvolvimento</h4>
              <p>São Paulo como uma nação próspera e desenvolvida, livre de amarras federais.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Auth Page
const AuthPage = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [message, setMessage] = useState('');
  const { login, register } = React.useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = isLogin ? await login(username, password) : await register(username, password);
    
    if (success) {
      navigate('/forum');
    } else {
      setMessage(isLogin ? 'Erro no login. Verifique suas credenciais.' : 'Erro no cadastro. Tente novamente.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-tabs">
          <button 
            className={`tab ${isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(true)}
          >
            Entrar
          </button>
          <button 
            className={`tab ${!isLogin ? 'active' : ''}`}
            onClick={() => setIsLogin(false)}
          >
            Cadastrar
          </button>
        </div>
        
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label>Nome de usuário:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          
          <div className="form-group">
            <label>Senha:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          
          <button type="submit" className="btn btn-primary">
            {isLogin ? 'Entrar' : 'Cadastrar'}
          </button>
        </form>
        
        {message && <p className="message error">{message}</p>}
        
        <div className="anonymous-note">
          <p>💡 <strong>Dica:</strong> Você também pode participar do fórum anonimamente, sem fazer login!</p>
        </div>
      </div>
    </div>
  );
};

// Forum Page
const ForumPage = () => {
  const [threads, setThreads] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  
  useEffect(() => {
    fetchThreads();
  }, []);

  const fetchThreads = async () => {
    try {
      const response = await axios.get(`${API}/threads`);
      setThreads(response.data);
    } catch (error) {
      console.error('Error fetching threads:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  return (
    <div className="forum-page">
      <div className="forum-header">
        <h2>Fórum da Brigada Paulista</h2>
        <button 
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="btn btn-primary"
        >
          {showCreateForm ? 'Cancelar' : 'Novo Tópico'}
        </button>
      </div>

      {showCreateForm && (
        <CreateThreadForm 
          onThreadCreated={() => {
            setShowCreateForm(false);
            fetchThreads();
          }} 
        />
      )}

      <div className="threads-list">
        {threads.map(thread => (
          <div key={thread.id} className="thread-item">
            <div className="thread-info">
              <Link to={`/thread/${thread.id}`} className="thread-title">
                {thread.title}
              </Link>
              <div className="thread-meta">
                <span className="author">
                  Por: {thread.author_username || 'Anônimo'}
                </span>
                <span className="date">{formatDate(thread.created_at)}</span>
                <span className="replies">{thread.reply_count} respostas</span>
              </div>
              <p className="thread-preview">{thread.content.substring(0, 200)}...</p>
            </div>
            {thread.image_data && (
              <div className="thread-image">
                <img src={`data:image/png;base64,${thread.image_data}`} alt="Thread image" />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

// Create Thread Form
const CreateThreadForm = ({ onThreadCreated }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [imageFile, setImageFile] = useState(null);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const { user } = React.useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      let imageData = null;
      let imageFilename = null;

      if (imageFile) {
        const formData = new FormData();
        formData.append('file', imageFile);
        const uploadResponse = await axios.post(`${API}/upload-image`, formData);
        imageData = uploadResponse.data.image_data;
        imageFilename = uploadResponse.data.filename;
      }

      const threadData = {
        title,
        content,
        image_data: imageData,
        image_filename: imageFilename
      };

      if (!isAnonymous && user) {
        threadData.author_username = user.username;
      }

      await axios.post(`${API}/threads`, threadData);
      setTitle('');
      setContent('');
      setImageFile(null);
      onThreadCreated();
    } catch (error) {
      console.error('Error creating thread:', error);
    }
  };

  return (
    <div className="create-thread-form">
      <h3>Criar Novo Tópico</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Título:</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Conteúdo:</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={6}
            required
          />
        </div>
        
        <div className="form-group">
          <label>Imagem (opcional):</label>
          <input
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files[0])}
          />
        </div>

        {user && (
          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={isAnonymous}
                onChange={(e) => setIsAnonymous(e.target.checked)}
              />
              Postar anonimamente
            </label>
          </div>
        )}
        
        <button type="submit" className="btn btn-primary">Criar Tópico</button>
      </form>
    </div>
  );
};

// Thread Detail Page
const ThreadPage = () => {
  const { threadId } = useParams();
  const [thread, setThread] = useState(null);
  const [replies, setReplies] = useState([]);
  const [replyContent, setReplyContent] = useState('');
  const [replyImageFile, setReplyImageFile] = useState(null);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const { user } = React.useContext(AuthContext);

  useEffect(() => {
    fetchThread();
    fetchReplies();
  }, [threadId]);

  const fetchThread = async () => {
    try {
      const response = await axios.get(`${API}/threads/${threadId}`);
      setThread(response.data);
    } catch (error) {
      console.error('Error fetching thread:', error);
    }
  };

  const fetchReplies = async () => {
    try {
      const response = await axios.get(`${API}/threads/${threadId}/replies`);
      setReplies(response.data);
    } catch (error) {
      console.error('Error fetching replies:', error);
    }
  };

  const handleReplySubmit = async (e) => {
    e.preventDefault();
    
    try {
      let imageData = null;
      let imageFilename = null;

      if (replyImageFile) {
        const formData = new FormData();
        formData.append('file', replyImageFile);
        const uploadResponse = await axios.post(`${API}/upload-image`, formData);
        imageData = uploadResponse.data.image_data;
        imageFilename = uploadResponse.data.filename;
      }

      const replyData = {
        content: replyContent,
        image_data: imageData,
        image_filename: imageFilename
      };

      if (!isAnonymous && user) {
        replyData.author_username = user.username;
      }

      await axios.post(`${API}/threads/${threadId}/replies`, replyData);
      setReplyContent('');
      setReplyImageFile(null);
      fetchReplies();
      fetchThread(); // Update reply count
    } catch (error) {
      console.error('Error creating reply:', error);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('pt-BR');
  };

  if (!thread) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="thread-page">
      <div className="thread-header">
        <Link to="/forum" className="back-link">← Voltar ao Fórum</Link>
        <h2>{thread.title}</h2>
      </div>

      <div className="thread-content">
        <div className="post original-post">
          <div className="post-header">
            <span className="author">{thread.author_username || 'Anônimo'}</span>
            <span className="date">{formatDate(thread.created_at)}</span>
            <span className="post-number">#1</span>
          </div>
          <div className="post-content">
            <p>{thread.content}</p>
            {thread.image_data && (
              <img 
                src={`data:image/png;base64,${thread.image_data}`} 
                alt="Post image" 
                className="post-image"
              />
            )}
          </div>
        </div>

        <div className="replies-section">
          {replies.map((reply, index) => (
            <div key={reply.id} className="post reply-post">
              <div className="post-header">
                <span className="author">{reply.author_username || 'Anônimo'}</span>
                <span className="date">{formatDate(reply.created_at)}</span>
                <span className="post-number">#{index + 2}</span>
              </div>
              <div className="post-content">
                <p>{reply.content}</p>
                {reply.image_data && (
                  <img 
                    src={`data:image/png;base64,${reply.image_data}`} 
                    alt="Reply image" 
                    className="post-image"
                  />
                )}
              </div>
            </div>
          ))}
        </div>

        <div className="reply-form">
          <h3>Responder</h3>
          <form onSubmit={handleReplySubmit}>
            <div className="form-group">
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                placeholder="Digite sua resposta..."
                rows={4}
                required
              />
            </div>
            
            <div className="form-group">
              <label>Imagem (opcional):</label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setReplyImageFile(e.target.files[0])}
              />
            </div>

            {user && (
              <div className="form-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={isAnonymous}
                    onChange={(e) => setIsAnonymous(e.target.checked)}
                  />
                  Responder anonimamente
                </label>
              </div>
            )}
            
            <button type="submit" className="btn btn-primary">Responder</button>
          </form>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Header />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/auth" element={<AuthPage />} />
              <Route path="/forum" element={<ForumPage />} />
              <Route path="/thread/:threadId" element={<ThreadPage />} />
            </Routes>
          </main>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;