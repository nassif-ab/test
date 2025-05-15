import React, { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import Header from "./components/Header";
import PostsList from "./components/PostsList";
import PostCard from "./components/PostCard";
import PostDetail from "./pages/PostDetail";
import { getPosts, PostUI, getUserRecommendations } from "./services/api";
import { useAuth } from "./content/AuthProvider";
import { LoginModalProvider } from "./content/LoginModalContext";


function App() {
  const { token, isAuthenticated, user } = useAuth();
  const [posts, setPosts] = useState<PostUI[]>([]);
  const [loading, setLoading] = useState(false);
  const [recommendations, setRecommendations] = useState<PostUI[]>([]);

  useEffect(() => {
    const fetchPosts = async () => {
      try {
        setLoading(true);
        const fetchedPosts = await getPosts(token || undefined);
        if (fetchedPosts && fetchedPosts.length > 0) {
          setPosts(fetchedPosts.map(post => ({
            id: post.id,
            titre: post.title,
            image: post.image || "/post.jpg",
            contenu: post.content,
            isliked: post.isliked || false,
            likes: post.likes || 0,
            visits: post.visits || 0,
            categorie: post.categorie || ""
          })));
        }
      } catch (error) {
        console.error('Error fetching posts:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPosts();
  }, [token]);

  useEffect(() => {
    if (token) {
    const fetchRecommendations = async () => {
      console.log("Estado de autenticación:", isAuthenticated);
      console.log("Usuario:", user);
      
      if (isAuthenticated && user?.id) {
        try {
          console.log("Obteniendo recomendaciones para el usuario ID:", user.id);
          const userRecommendations = await getUserRecommendations(user.id, token);
          console.log("Recomendaciones recibidas:", userRecommendations);
          setRecommendations(userRecommendations);
        } catch (error) {
          console.error("Error al obtener recomendaciones:", error);
        }
      } else {
        console.log("No se obtuvieron recomendaciones: usuario no autenticado o sin ID");
      }
    };
    
    fetchRecommendations();
    }
  }, [isAuthenticated, user, token]);

  return (
      <Router>
        <LoginModalProvider>
          <div className="min-h-screen bg-gray-50">
            <Header />
          
          <Routes>
            <Route path="/" element={
            <>

{isAuthenticated && recommendations.length > 0 && (
  <div className="container mx-auto px-4 py-8">
    <h2 className="text-2xl font-bold mb-6 text-center text-[#063267]">Recommandé pour vous</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
      {recommendations.map((post, index) => (
        <PostCard 
          key={index}
          id={post.id}
          titre={post.titre}
          image={post.image}
          contenu={post.contenu}
          isliked={post.isliked}
          likes={post.likes}
          visits={post.visits}
          categorie={post.categorie}
        />
      ))}
    </div>
  </div>
)}
              {/* HERO SHORTCUT CARDS */}
              <section className="mt-6 flex flex-wrap gap-6 justify-center px-4">
                {[
                  {
                    label: "Services numériques",
                    desc: "Outils et plateformes.",
                    icon: (
                      <svg
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                        className="w-10 h-10"
                      >
                        <circle cx="12" cy="12" r="10" />
                      </svg>
                    ),
                  },
                  {
                    label: "Avis aux étudiants",
                    desc: "Annonces et informations.",
                    icon: (
                      <svg
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                        className="w-10 h-10"
                      >
                        <path d="M5 13l4 4L19 7" />
                      </svg>
                    ),
                  },
                  {
                    label: "Emplois du temps",
                    desc: "Les plannings de cours.",
                    icon: (
                      <svg
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                        className="w-10 h-10"
                      >
                        <rect width="18" height="14" x="3" y="5" rx="2" />
                        <path d="M16 3v4M8 3v4M3 9h18" />
                      </svg>
                    ),
                  },
                  {
                    label: "Nos formations",
                    desc: "Cursus et spécialités.",
                    icon: (
                      <svg
                        fill="none"
                        stroke="currentColor"
                        strokeWidth={2}
                        viewBox="0 0 24 24"
                        className="w-10 h-10"
                      >
                        <path d="M12 20h9" />
                        <path d="M12 4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2" />
                        <rect width="12" height="16" x="2" y="4" rx="2" />
                      </svg>
                    ),
                  },
                ].map((card) => (
                  <div
                    key={card.label}
                    className="flex flex-col items-center gap-1 bg-white rounded-xl shadow-lg px-8 py-6 mb-4 min-w-[230px] max-w-[260px] flex-1 transition hover:scale-[1.02]"
                  >
                    <span className="text-[#063267] mb-2">{card.icon}</span>
                    <h3 className="font-semibold text-lg text-[#063267]">{card.label}</h3>
                    <p className="text-gray-500 text-sm text-center">{card.desc}</p>
                  </div>
                ))}
              </section>
            
              {/* المنشورات */}
              <PostsList posts={posts} />

            </>
          } />
          <Route path="/post/:id" element={<PostDetail />} />
          <Route path="*" element={<Navigate to="/" />} />
          
          </Routes>
          </div>
        </LoginModalProvider>
      </Router>
  );
}

export default App;