import Button from "@/components/Button";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center">
      
      {/* Title */}
      <h1 className="text-2xl font-semibold mt-10 mb-16">
        Healthcare application
      </h1>

      {/* Buttons */}
      <div className="flex gap-16">
        <Button label="Login" href="/auth/login" />
        <Button label="Register" href="/auth/register" />
      </div>

    </main>
  );
}