export default function ProductCard({ product, handleLike, errorMessage }) {
  const likeText =
    product.likes === 1 ? "1 Like" : `${product.likes ?? 0} Likes`;

  return (
    <div className="group max-w-xs overflow-hidden rounded-xl border bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-lg">
      <div className="h-48 overflow-hidden bg-gray-100">
        <img
          src={product.image || "/placeholder.png"}
          alt={product.title}
          className="h-full w-full object-cover transition duration-300 group-hover:scale-105"
        />
      </div>

      <div className="p-4">
        <h2 className="line-clamp-1 text-lg font-bold text-gray-800">
          {product.title}
        </h2>

        <div className="mt-4 flex items-center justify-between">
          <button
            onClick={() => handleLike(product.id)}
            className="rounded-xl bg-blue-500 px-5 py-2 text-white transition hover:bg-blue-600 active:scale-95"
            aria-label={`Like ${product.title}`}
          >
            👍 Like
          </button>

          <span className="text-sm font-medium text-gray-600">{likeText}</span>
        </div>

        {errorMessage && (
          <p className="mt-3 rounded bg-red-50 p-2 text-sm text-red-500">
            {errorMessage}
          </p>
        )}
      </div>
    </div>
  );
}
