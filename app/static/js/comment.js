// Đặt ngôn ngữ là tiếng Việt
moment.locale('vi');

// Duyệt qua tất cả các thẻ có class 'date'
document.querySelectorAll('.date').forEach(function(element) {
// Lấy giá trị từ thuộc tính data-time
const originalTime = element.getAttribute('data-time');
if (originalTime) {
    // Chuyển đổi thời gian sang định dạng "3 giờ trước", "2 ngày trước"
    const relativeTime = moment(originalTime).fromNow();
    // Cập nhật nội dung hiển thị
    element.textContent = relativeTime;
}
});

function addComment() {
    const content = document.getElementById("comments").value.trim();
    if (!content) {
        alert("Nội dung bình luận không được để trống!");
        return;
    }
    fetch('/api/comments', {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error('HTTP error! status: ${response.status}');
        }
        return response.json();
    })
    .then((data) => {
        // Thêm bình luận mới vào carousel
        const commentsList = document.getElementById("comments-list");
        commentsList.innerHTML='';
        commentsList = `
            <div class="carousel-item ">
                <h4 class="text-danger fs-3 fw-bold text-center ">"${data.content}"<br>
                    <span class="fs-4 fw-bold d-block">
                        ${data.name ? '${data.name}' : 'Ẩn danh'}
                        - <em class="date" data-time="${data.time}">${moment(data.time).fromNow()}</em>
                    </span>
                </h4>
            </div>
        `;
        commentsList.innerHTML += newComment;

        // Reset textarea
        document.getElementById("comments").value = "";
    })
    .catch((error) => {
        console.error("Error adding comment:", error);
        alert("Không thể gửi bình luận. Vui lòng thử lại.");
    });
}