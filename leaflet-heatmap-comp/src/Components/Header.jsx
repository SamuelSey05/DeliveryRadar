import "./Header.css";

function Header() {
  return (
    <div className="navbar" data-bs-theme="dark">
      <ul>
        <li className="nav-link">
          <a href="#">Take a Video</a>
        </li>
        <li className="nav-link">
          <a href="#">Heatmap</a>
        </li>
      </ul>
    </div>
  );
}

export default Header;
