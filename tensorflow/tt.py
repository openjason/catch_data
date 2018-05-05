import tensorflow as tf

a = tf.constant([1.0,2.1,4.3],name='a')
b = tf.constant([2.0,3.0,3.3],name='b')
c = tf.constant([2.0,3.0,3.3],name='c')
result = a + b +c

print(result)

sess = tf.Session()
re = sess.run(result)
#re = tf.Session.run(result)
print (re)