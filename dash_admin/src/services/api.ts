import axiosClient from "./axiosclient";

// Interfaces de données
export interface User {
  id: string;
  username: string;
  email?: string;
  created_at?: string;
  is_admin?: boolean;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  image?: string;
  categorie?: string;
  isliked?: boolean;
  likes?: number;
  visits?: number;
  user_id?: number;
  created_at?: string;
}

// Interfaz para los posts formateados para el frontend
export interface PostUI {
  id: string;
  titre: string;
  image: string;
  contenu: string;
  isliked: boolean;
  likes: number;
  visits: number;
  categorie?: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  username: string;
  is_admin: boolean;
  user?: User;
}


// Connexion
export const loginUser = async (username: string, password: string): Promise<AuthResponse> => {
  try {
    console.log('Attempting to login with username:', username);
    console.log('API URL:', import.meta.env.VITE_API_URL);
    
    // استخدام نقطة نهاية المصادقة الجديدة
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    console.log('Sending login request...');
    const response = await axiosClient.post("/auth/token_admin", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('Login successful, token received');
    console.log('Token:', response.data.access_token);
    console.log('User data from token:', {
      user_id: response.data.user_id,
      username: response.data.username,
      is_admin: response.data.is_admin
    });

    // Crear un objeto de usuario a partir de los datos recibidos
    const user: User = {
      id: response.data.user_id.toString(),
      username: response.data.username,
      is_admin: response.data.is_admin
    };

    return {
      ...response.data,
      user
    };
  } catch (error: any) {
    console.error('Login error details:', error);
    
    if (error.response) {
      // الخادم استجاب بكود حالة خارج نطاق 2xx
      console.error('Error response status:', error.response.status);
      console.error('Error response data:', error.response.data);
      
      const status = error.response.status;
      if (status === 404) throw new Error("Utilisateur introuvable");
      if (status === 401) throw new Error("Mot de passe incorrect");
      throw new Error(`Erreur du serveur: ${error.response.data.detail || 'Erreur inconnue'}`);
    } else if (error.request) {
      // تم إجراء الطلب ولكن لم يتم استلام استجابة
      console.error('No response received from server');
      throw new Error("Aucune réponse reçue du serveur. Assurez-vous que le serveur backend est en cours d'exécution.");
    } else {
      // حدث خطأ أثناء إعداد الطلب
      console.error('Error setting up request:', error.message);
      throw new Error(`Erreur lors de la configuration de la requête: ${error.message}`);
    }
  }
};


export const registerUser = async (username: string, email: string, password: string): Promise<User> => {
  try {
    // استخدام نقطة نهاية التسجيل الجديدة
    const response = await axiosClient.post("/auth/register", {
      username,
      email,
      password,
    });

    return response.data;
  } catch (error: any) {
    const status = error.response?.status;
    if (status === 400) throw new Error("المستخدم موجود بالفعل");
    throw new Error("فشل في الاتصال بالخادم");
  }
};


export const getPost = async (id: string, token: string): Promise<Post> => {
  try {
    const response = await axiosClient.get(`/posts/${id}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الاتصال بالخادم");
  }
};

export const getPosts = async (token?: string): Promise<Post[]> => {
  try {
    const config = token ? {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    } : {};
    
    const response = await axiosClient.get("/posts", config);
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الاتصال بالخادم");
  }
};


// Función para obtener los detalles de un post específico
export const getPostById = async (postId: string | number, token?: string): Promise<Post | null> => {
  try {
    const numericId = typeof postId === 'string' ? parseInt(postId, 10) : postId;
    
    // Configurar headers con o sin token de autenticación
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await axiosClient.get(`/posts/${numericId}`, { headers });
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener post por ID:', error);
    return null;
  }
};

// إنشاء منشور جديد
export const createPost = async (post: { title: string, content: string, categorie?: string, image?: string }, token: string): Promise<Post> => {
  try {
    const response = await axiosClient.post('/posts', post, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في إنشاء المنشور");
  }
};

// الحصول على جميع المستخدمين (للمسؤول فقط)
export const getUsers = async (token: string): Promise<User[]> => {
  try {
    const response = await axiosClient.get('/users', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الحصول على المستخدمين");
  }
};

// الحصول على إحصائيات المستخدم
export interface UserStats {
  user_id: string;
  username: string;
  total_posts: number;
  total_likes: number;
  total_visits: number;
  favorite_categories: {category: string, count: number}[];
}

export const getUserStats = async (userId: string, token: string): Promise<UserStats> => {
  try {
    const response = await axiosClient.get(`/users/${userId}/stats`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الحصول على إحصائيات المستخدم");
  }
};

// الحصول على إحصائيات المنشورات
export interface PostStats {
  total_posts: number;
  total_likes: number;
  total_visits: number;
  popular_categories: {category: string, count: number}[];
  most_liked_posts: Post[];
  most_visited_posts: Post[];
}

export const getPostStats = async (token: string): Promise<PostStats> => {
  try {
    const response = await axiosClient.get('/posts/stats', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الحصول على إحصائيات المنشورات");
  }
};

// حذف منشور
export const deletePost = async (postId: string, token: string): Promise<void> => {
  try {
    await axiosClient.delete(`/posts/${postId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
  } catch (error: any) {
    throw new Error("فشل في حذف المنشور");
  }
};

// تحديث منشور
export const updatePost = async (postId: string, postData: Partial<Post>, token: string): Promise<Post> => {
  try {
    const response = await axiosClient.put(`/posts/${postId}`, postData, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في تحديث المنشور");
  }
};

