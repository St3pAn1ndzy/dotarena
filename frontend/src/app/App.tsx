import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from '../pages/HomePage/HomePage.tsx'
import ProfilePage from '../pages/ProfilePage/ProfilePage.tsx'
import BattlePage from '../pages/BattlePage/BattlePage.tsx'

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

export default App