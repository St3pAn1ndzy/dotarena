import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage/HomePage.tsx'
import ProfilePage from './pages/ProfilePage/ProfilePage.tsx'
import BattlePage from './pages/BattlePage/BattlePage.tsx'
import './index.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/profile/:steamId" element={<ProfilePage />} />
        <Route path="/battle/:id" element={<BattlePage />} />
      </Routes>
    </BrowserRouter>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)