export default function ProductCard({ product, handleLike }) {
  return (
    <div className="max-w-xs rounded-lg border bg-white p-4 shadow">
      <img
        src={product.image}
        alt={product.title}
        className="h-48 w-full rounded object-cover"
      />

      <h2 className="mt-3 text-lg font-semibold">{product.title}</h2>

      <div className="mt-4 flex items-center justify-between">
        <button
          onClick={() => handleLike(product.id)}
          className="rounded bg-blue-500 px-4 py-2 text-white hover:bg-blue-600"
        >
          Like
        </button>

        <span className="font-medium">Likes: {product.likes}</span>
      </div>
    </div>
  );
}
