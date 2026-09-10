# Java 架构检查清单

## 1. 分层架构（Spring Boot）

### 标准分层
```
┌─────────────────────────────────────┐
│         Controller Layer            │  REST API 入口
├─────────────────────────────────────┤
│        Service Layer                │  业务逻辑
├─────────────────────────────────────┤
│      Repository Layer               │  数据访问
├─────────────────────────────────────┤
│         Domain Model                │  实体和值对象
└─────────────────────────────────────┘
```

检查项：
- [ ] Controller 是否只负责参数绑定和响应格式化
- [ ] Service 是否包含所有业务逻辑
- [ ] Repository 是否只负责数据访问
- [ ] 是否避免了跨层调用

```java
// ❌ 坏：Controller 包含业务逻辑
@RestController
public class OrderController {
    @PostMapping("/orders")
    public Order createOrder(@RequestBody CreateOrderRequest req) {
        // 业务逻辑放在 controller 里
        Order order = new Order();
        order.setTotal(calculateTotal(req.getItems()));
        order.setStatus(OrderStatus.PENDING);
        // ... 更多业务逻辑
        return orderRepository.save(order);
    }
}

// ✅ 好：Controller 只做编排
@RestController
public class OrderController {
    private final OrderService orderService;

    @PostMapping("/orders")
    public OrderResponse createOrder(@Valid @RequestBody CreateOrderRequest req) {
        Order order = orderService.createOrder(req);
        return OrderResponse.from(order);
    }
}
```

## 2. 依赖注入

- [ ] 是否使用构造器注入而非字段注入
- [ ] 是否避免了 `@Autowired` 字段注入
- [ ] Bean 的生命周期是否正确管理

```java
// ❌ 坏：字段注入
@Service
public class OrderService {
    @Autowired
    private OrderRepository repository;  // 难以测试
}

// ✅ 好：构造器注入
@Service
public class OrderService {
    private final OrderRepository repository;
    private final PaymentGateway paymentGateway;

    public OrderService(OrderRepository repository, PaymentGateway paymentGateway) {
        this.repository = repository;
        this.paymentGateway = paymentGateway;
    }
}
```

## 3. 异常处理

- [ ] 是否使用了统一的异常处理（`@ControllerAdvice`）
- [ ] 业务异常是否继承自统一的基类
- [ ] 是否避免了在业务逻辑中捕获 RuntimeException

```java
// ✅ 统一的异常层次
public class DomainException extends RuntimeException {
    private final String code;
    public DomainException(String code, String message) {
        super(message);
        this.code = code;
    }
}

public class InsufficientFundsException extends DomainException {
    public InsufficientFundsException(BigDecimal shortfall) {
        super("INSUFFICIENT_FUNDS", String.format("Short by %.2f", shortfall));
    }
}

// ✅ 统一的异常处理器
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(DomainException.class)
    public ResponseEntity<ErrorResponse> handleDomainException(DomainException e) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse(e.getCode(), e.getMessage()));
    }
}
```

## 4. 事务管理

- [ ] 是否在 Service 层使用 `@Transactional`
- [ ] 是否避免了在 Controller 层管理事务
- [ ] 事务传播级别是否正确设置

```java
@Service
public class PaymentService {
    @Transactional
    public PaymentResult processPayment(PaymentRequest request) {
        // 所有数据库操作在同一事务中
        Order order = orderRepository.findById(request.orderId())
            .orElseThrow(() -> new NotFoundException("Order not found"));

        Payment payment = paymentGateway.charge(request.amount());
        orderRepository.updateStatus(order.getId(), OrderStatus.PAID);

        return PaymentResult.success(payment.getId());
    }
}
```

## 5. 测试

- [ ] 单元测试是否使用了 `@ExtendWith(MockitoExtension.class)`
- [ ] 集成测试是否使用了 `@SpringBootTest`
- [ ] 是否使用了 `@DataJpaTest` 进行 Repository 测试

## 6. 代码规范

- [ ] 是否遵循 Google Java Style Guide 或项目约定
- [ ] 日志是否使用了 SLF4J 而非 `System.out.println`
- [ ] 是否使用了记录类（Java 16+）简化数据类
