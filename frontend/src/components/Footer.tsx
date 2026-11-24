export default function Footer() {
  return (
    <footer className="border-t bg-white px-6 py-6 text-center text-sm text-gray-500">
      <p>
        &copy; {new Date().getFullYear()} Eventify.
        All rights reserved.
      </p>

      <p className="mt-1">
        Discover events. Book tickets. Make memories.
      </p>
    </footer>
  );
}