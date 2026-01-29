import axios from "axios";

const API = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL
});

// 🔥 Attach token to EVERY request
API.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("admin_token");

    if (token) {
      config.headers["X-Admin-Token"] = token;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// 🔥 Auto-logout on 401
API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("admin_token");
      window.location.reload(); // force back to login
    }
    return Promise.reject(error);
  }
);

export const getStudents = () => API.get("/admin/students");

export const addStudent = (student_id, name) =>
  API.post(`/admin/students?student_id=${student_id}&name=${name}`);

export const updateStudent = (id, name) =>
  API.put(`/admin/students/${id}?name=${name}`);

export const deleteStudent = (id) =>
  API.delete(`/admin/students/${id}`);

export const addMarks = (student_id, subject, score) =>
  API.post(`/admin/marks?student_id=${student_id}&subject=${subject}&score=${score}`);

export const getReport = (id) =>
  API.get(`/admin/report/${id}`);

export const addAttendance = (student_id, date, status) =>
  API.post(
    `/admin/attendance?student_id=${student_id}&date=${date}&status=${status}`
  );

// ---------------- ATTENDANCE ANALYTICS ----------------

export const getAttendanceSummary = (studentId) => {
  return API.get(`/admin/attendance/summary/${studentId}`);
};

export const getAttendanceMonth = (studentId, year, month) => {
  return API.get(
    `/admin/attendance/month/${studentId}?year=${year}&month=${month}`
  );
};

export const exportAttendance = (studentId) => {
  return API.get(`/admin/attendance/export/${studentId}`, {
    responseType: "blob"
  });
};
