export default function ProductCard({ product, handleLike, errorMessage }) {
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
          className="bg-blue-500 px-6 py-2 rounded-xl"
        >
          Like
        </button>
        <span className="font-medium">Likes: {product.likes}</span>
      </div>
      {errorMessage && (
        <p className="mt-2 text-sm text-red-500">{errorMessage}</p>
      )}
    </div>
  );
}
