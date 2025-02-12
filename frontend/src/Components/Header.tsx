import React from "react";
import "./Header.css";

function Header() {
  return (
    <nav
      className="navbar bg-dark border-bottom border-body"
      data-bs-theme="dark"
    >
      <div className="container">
        <a className="nav-link" href="#">
          Take a Video
        </a>
        <a className="nav-link" href="#">
          Heatmap
        </a>
      </div>
    </nav>
  );
}

export default Header;
