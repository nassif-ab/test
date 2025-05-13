import React from 'react';
import PostCard from './PostCard';
import { PostUI } from '../services/api';

interface PostsListProps {
  posts: PostUI[];
}

const PostsList: React.FC<PostsListProps> = ({ posts }) => {
  return (
    <div className="container mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold mb-8 text-center text-[#063267]">Derniers Articles</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {posts.map((post, index) => (
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
  );
};

export default PostsList;
