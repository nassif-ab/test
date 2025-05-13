import axiosClient from "./axiosclient";

// واجهات البيانات
interface User {
  id: string;
  username: string;
  email?: string;
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
  user: User;
}


// تسجيل الدخول
export const loginUser = async (username: string, password: string): Promise<AuthResponse> => {
  try {
    console.log('Attempting to login with username:', username);
    console.log('API URL:', import.meta.env.VITE_API_URL);
    
    // استخدام نقطة نهاية المصادقة الجديدة
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    console.log('Sending login request...');
    const response = await axiosClient.post("/auth/token", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    
    console.log('Login successful, token received');
    console.log('Token:', response.data.access_token);

    // الحصول على معلومات المستخدم بعد تسجيل الدخول
    console.log('Fetching user information...');
    const userResponse = await axiosClient.get("/auth/me", {
      headers: {
        'Authorization': `Bearer ${response.data.access_token}`
      }
    });
    
    console.log('User information received:', userResponse.data);

    return {
      ...response.data,
      user: userResponse.data
    };
  } catch (error: any) {
    console.error('Login error details:', error);
    
    if (error.response) {
      // الخادم استجاب بكود حالة خارج نطاق 2xx
      console.error('Error response status:', error.response.status);
      console.error('Error response data:', error.response.data);
      
      const status = error.response.status;
      if (status === 404) throw new Error("المستخدم غير موجود");
      if (status === 401) throw new Error("كلمة المرور غير صحيحة");
      throw new Error(`خطأ من الخادم: ${error.response.data.detail || 'خطأ غير معروف'}`);
    } else if (error.request) {
      // تم إجراء الطلب ولكن لم يتم استلام استجابة
      console.error('No response received from server');
      throw new Error("لم يتم استلام استجابة من الخادم. تأكد من تشغيل الخادم الخلفي.");
    } else {
      // حدث خطأ أثناء إعداد الطلب
      console.error('Error setting up request:', error.message);
      throw new Error(`خطأ في إعداد الطلب: ${error.message}`);
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

// الحصول على منشورات المستخدم الحالي
export const getMyPosts = async (token: string): Promise<Post[]> => {
  try {
    const response = await axiosClient.get("/posts/my-posts", {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error: any) {
    throw new Error("فشل في الاتصال بالخادم");
  }
};


export const likePost = async (postId: string | number, token: string): Promise<void> => {
  try {
    console.log('likePost llamado con postId:', postId, 'tipo:', typeof postId);
    // Asegurarnos de que el ID es un número para la API
    const numericId = typeof postId === 'string' ? parseInt(postId, 10) : postId;
    console.log('URL de la petición:', `/posts/${numericId}/like`);
    
    await axiosClient.post(`/posts/${numericId}/like`, {}, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('Petición de like completada con éxito');
  } catch (error: any) {
    console.error('Error en likePost:', error);
    throw new Error("فشل في الاتصال بالخادم");
  }
};

// Función para registrar una visita a un post
export const recordVisit = async (postId: string | number, token?: string): Promise<void> => {
  try {
    // Asegurarnos de que el ID es un número para la API
    const numericId = typeof postId === 'string' ? parseInt(postId, 10) : postId;
    
    // Configurar headers con o sin token de autenticación
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    await axiosClient.post(`/posts/${numericId}/visit`, {}, { headers });
    console.log('Visita registrada para el post ID:', numericId);
  } catch (error: any) {
    console.error('Error al registrar visita:', error);
    // No lanzamos error para que no afecte a la experiencia del usuario
  }
};

// Función para obtener el número de visitas de un post
export const getPostVisits = async (postId: string | number): Promise<number> => {
  try {
    const numericId = typeof postId === 'string' ? parseInt(postId, 10) : postId;
    const response = await axiosClient.get(`/posts/${numericId}/visits`);
    return response.data;
  } catch (error: any) {
    console.error('Error al obtener visitas:', error);
    return 0; // Devolver 0 por defecto en caso de error
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
export const createPost = async (post: { title: string, content: string }, token: string): Promise<Post> => {
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

// Función para obtener recomendaciones para un usuario
export const getUserRecommendations = async (userId: string | number, token?: string): Promise<PostUI[]> => {
  try {
    console.log("getUserRecommendations llamada con userId:", userId, "y token:", token ? "token presente" : "sin token");
    const numericId = typeof userId === 'string' ? parseInt(userId, 10) : userId;
    
    // Configurar headers con o sin token de autenticación
    const headers: Record<string, string> = {};
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
      console.log("Token añadido a los headers");
    } else {
      console.log("No hay token disponible para la solicitud");
    }
    
    console.log(`Realizando solicitud GET a /posts/user/${numericId}/recommendations`);
    const response = await axiosClient.get(`/posts/user/${numericId}/recommendations`, { headers });
    console.log("Respuesta recibida:", response.data);
    
    if (!response.data || !Array.isArray(response.data) || response.data.length === 0) {
      console.log("No se recibieron recomendaciones o el formato es incorrecto");
      return [];
    }
    
    // Convertir la respuesta al formato PostUI
    const recommendations = response.data.map((post: any) => ({
      id: post.id,
      titre: post.title,
      image: post.image || "/post.jpg",
      contenu: post.content,
      isliked: false, // Por defecto no sabemos si le gustó
      likes: 0,       // No tenemos esta información aquí
      visits: 0,      // No tenemos esta información aquí
      categorie: post.categorie
    }));
    
    console.log(`Se procesaron ${recommendations.length} recomendaciones`);
    return recommendations;
  } catch (error: any) {
    console.error('Error al obtener recomendaciones:', error);
    return [];
  }
};

// Función para obtener posts similares a un post específico
export const getSimilarPosts = async (postId: string | number): Promise<PostUI[]> => {
  try {
    const numericId = typeof postId === 'string' ? parseInt(postId, 10) : postId;
    const response = await axiosClient.get(`/posts/${numericId}/similar`);
    
    // Convertir la respuesta al formato PostUI
    return response.data.map((post: any) => ({
      id: post.id,
      titre: post.title,
      image: post.image || "/post.jpg",
      contenu: post.content,
      isliked: false, // Por defecto no sabemos si le gustó
      likes: 0,       // No tenemos esta información aquí
      visits: 0,      // No tenemos esta información aquí
      categorie: post.categorie
    }));
  } catch (error: any) {
    console.error('Error al obtener posts similares:', error);
    return [];
  }
};