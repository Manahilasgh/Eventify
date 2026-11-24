import api from "@/lib/api";

interface OrganizerApplication {
  organization_name: string;
  description: string;
}

export const applyOrganizer = async (
  data: OrganizerApplication
) => {
  const response = await api.post(
    "/api/auth/apply-organizer/",
    data
  );

  return response.data;
};