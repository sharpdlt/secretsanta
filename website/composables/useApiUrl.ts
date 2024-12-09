export const useApiUrl = () => {
    return (path: string) => `${config.public.apiBase}${path}`;
};
