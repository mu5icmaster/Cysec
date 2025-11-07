function Loader() {
  return (
    <div className="flex items-center justify-center">
      <div className="flex flex-row gap-2">
        <div className="h-4 w-4 animate-bounce rounded-full bg-red-600"></div>
        <div className="h-4 w-4 animate-bounce rounded-full bg-red-600 [animation-delay:-.3s]"></div>
        <div className="h-4 w-4 animate-bounce rounded-full bg-red-600 [animation-delay:-.5s]"></div>
      </div>
    </div>
  );
}

export default Loader;
