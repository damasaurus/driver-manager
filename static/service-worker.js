self.addEventListener("message", function (event) {
    const data = event.data;
    const title = data.title || "Driver Update";
    const options = {
      body: data.body,
      icon: "/static/icons/icon-192.png",
    };
    self.registration.showNotification(title, options);
  });
  