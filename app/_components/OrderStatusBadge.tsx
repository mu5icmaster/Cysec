function OrderStatusBadge({
  status,
}: {
  status: "pending" | "sent" | "delivered";
}) {
  return (
    <>
      {status === "pending" && (
        <span className="text-md flex w-20 justify-center rounded-full bg-green-500 p-0.5 font-semibold uppercase tracking-tight text-stone-100 dark:bg-green-600">
          pending
        </span>
      )}
      {status === "sent" && (
        <span className="text-md flex w-20 justify-center rounded-full bg-yellow-500 p-0.5 font-semibold uppercase tracking-tight text-stone-100 dark:bg-yellow-600">
          sent
        </span>
      )}
      {status === "delivered" && (
        <span className="text-md flex w-24 justify-center rounded-full bg-red-500 p-0.5 font-semibold uppercase tracking-tight text-stone-100 dark:bg-red-600">
          delivered
        </span>
      )}
    </>
  );
}

export default OrderStatusBadge;
