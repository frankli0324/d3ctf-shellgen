#include <future>
int main() { std::promise<void>().get_future().wait(); }
