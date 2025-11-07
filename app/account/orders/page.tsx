import OrderItem from "@/app/_components/OrderItem";
import { getUserOrders } from "@/app/_lib/data_service";

async function Page() {
  const orders = (await getUserOrders()).filter(
    (order) => order.status === "pending" || order.status === "sent",
  );

  if (!orders.length) throw new Error("No orders found.");

  return (
    <ul className="flex flex-col gap-4">
      {orders.map((order) => (
        <OrderItem orderItem={order} key={order.id} />
      ))}
    </ul>
  );
}

export default Page;
